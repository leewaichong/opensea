# Slack app manifest:
# Socket Mode ON; bot scopes chat:write, im:write, im:history, commands,
# app_mentions:read; slash commands /premeeting, /premeeting-compile, /premeeting-scripted;
# subscribe to message.im.
#
# /premeeting hosts a DM setup flow. If the initiator @mentions teammates with roles
# (Growth/Commerce/Lead) in the setup, the bot DMs each of them, grounds their reply into
# that role's persona Stance, and auto-compiles the brief once all have replied (or the
# initiator DMs `compile` / runs /premeeting-compile). With no @mentions it stays solo
# (initiator voices every role). /premeeting-scripted is the fast cached fallback.
#
# Brief generation has two modes, gated on PMLE_LIVE_AGENTS:
#   default (unset/0): /premeeting collects the user's answers but the final brief is the
#                      deterministic cached Shopee digest (same output as /premeeting-scripted)
#                      — input-independent, safe for stage timing.
#   PMLE_LIVE_AGENTS=1: each stakeholder reply is grounded into that participant's Stance via
#                      their persistent agent, and the brief is classified live from the
#                      grounded stances. This is the only mode where the brief reflects what
#                      the user actually typed. Requires OPENAI_API_KEY; ~21 extra agent calls.
import os, asyncio, threading
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from pmle import manual_flow, meeting as meeting_mod, orchestrator
from pmle.data.cached_stances import CACHED
from pmle.data.agenda import AGENDA
from pmle.participants import build_participant
from pmle.schemas import ClassificationResult, Stance
from agents import Runner
from pmle.digest import render_blocks

load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN", "xoxb-import-smoke"),
          token_verification_enabled=False)
HUMAN = os.environ.get("PMLE_HUMAN_USER")
CHANNEL = os.environ.get("PMLE_MEETING_CHANNEL")
_CACHE = {(s.stakeholder, s.item_id): s for s in CACHED}
_MANUAL_SESSIONS: dict[str, dict] = {}
# Multi-participant meetings, keyed by initiator user id. _USER_TO_MEETING routes any
# participant's (or the initiator's) DM back to the meeting they belong to.
_PENDING_MEETINGS: dict[str, "meeting_mod.Meeting"] = {}
_USER_TO_MEETING: dict[str, str] = {}
# Serializes the compile trigger so concurrent participant replies can't double-post the brief.
_COMPILE_LOCK = threading.Lock()


async def _demo_ask_stance(person, item_id, item_text):
    return _CACHE.get((person, item_id)) or Stance(
        stakeholder=person,
        item_id=item_id,
        position="support",
        rationale="No known blocker.",
        key_assumptions=[],
    )


async def _demo_classify_item(stances):
    item = stances[0].item_id
    if item == "objective":
        return ClassificationResult(
            item_id=item,
            status="fake_agreement",
            summary="Everyone says younger shoppers, but success criteria differ.",
            divergence="Growth: acquisition and app installs; Commerce: GMV and voucher redemption; Campaign Lead: mainstream-safe youth reach",
            cited_stances=["Wai Chong", "Shang", "John Taylor"],
            follow_up="Decide whether the primary objective is acquisition, GMV, or brand reach.",
        )
    if item == "role-mix":
        return ClassificationResult(
            item_id=item,
            status="crux",
            summary="The creator role split is unresolved.",
            divergence="Wai Chong prefers Mika as hero face; Shang requires Jayden for Shopee Live conversion; John may split hero and conversion roles.",
            cited_stances=["Wai Chong", "Shang", "John Taylor"],
        )
    return ClassificationResult(
        item_id=item,
        status="agreed",
        summary="No blocking divergence found.",
        cited_stances=[s.stakeholder for s in stances],
    )

def _live_agents() -> bool:
    return os.environ.get("PMLE_LIVE_AGENTS") == "1"


def _ground_stance(person: str, text: str):
    """Map a stakeholder's free-form reply onto their structured Stance via their
    persistent agent (conversational contract editing). Returns the agent's confirmation
    so the bot's acknowledgement is grounded in what the human actually said.

    Offline (no live agents) this is a no-op: the seeded/cached stances stand in, and the
    handler falls back to a templated acknowledgement."""
    if not _live_agents():
        return None
    agent, session = build_participant(person)
    agenda_lines = "\n".join(f"- {a.id}: '{a.text}'" for a in AGENDA if a.id in ("objective", "role-mix"))
    prompt = (
        f"My input for the Shopee SG 11.11 creator-mix prep:\n{text}\n\n"
        "Map this onto my stance and persist it with set_stance, using EXACTLY these item_ids:\n"
        f"{agenda_lines}\n"
        "Then confirm in one or two sentences what you saved."
    )
    result = asyncio.run(Runner.run(agent, prompt, session=session))
    return result.final_output


def _build_board():
    """Generate the brief from the current stance store. Live agents read the grounded
    stances; otherwise the deterministic demo functions back the cached Shopee scenario."""
    if _live_agents():
        return asyncio.run(orchestrator.run_meeting())
    return asyncio.run(orchestrator.run_meeting(
        ask_stance=_demo_ask_stance, classify_item=_demo_classify_item))


def _post_board(board, *, say=None, respond=None):
    """Post the digest to the meeting channel, falling back to the current surface
    (DM `say` or slash `respond`) when the bot isn't in the channel."""
    text = f"Pre-meeting brief ready: {board.meeting_item_count()} items need the live meeting"
    blocks = render_blocks(board)
    surface = say or respond
    if not CHANNEL:
        surface(text=text, blocks=blocks)
        return
    try:
        client_post = app.client.chat_postMessage
        client_post(channel=CHANNEL, blocks=blocks, text=text)
        if say:
            say("Posted the compressed brief to the meeting channel.")
    except SlackApiError as exc:
        if exc.response.get("error") != "not_in_channel":
            raise
        surface(text=text, blocks=blocks)


def _handle_manual_turn(user, text, say, client):
    """Drive one DM turn of the hosted /premeeting flow.

    At the setup step, if the initiator @mentioned real participants, branch into the
    multi-participant flow (DM each of them); otherwise stay solo (initiator voices all)."""
    session = _MANUAL_SESSIONS[user]

    if session.get("step") == "setup":
        roster = meeting_mod.parse_participants(text, initiator=user)
        if roster:
            session.setdefault("inputs", {})["setup"] = text
            _start_multihuman(user, session, roster, say, client)
            return

    out = manual_flow.advance_manual_flow(session, text)

    if out["ground"]:
        person, reply_text = out["ground"]
        ack = _ground_stance(person, reply_text)
        say(ack or f"Captured {person}'s input.")

    if out["complete"]:
        say(out["reply"])
        board = _build_board()
        _post_board(board, say=say)
        _MANUAL_SESSIONS.pop(user, None)
    else:
        say(out["reply"])


# --- multi-participant flow: orchestrator DMs the real people and collects their input ---
# Opening DM to each participant — decoupled from the solo-flow prompts (which carry a
# "Thanks, I have the setup" preamble that reads wrong as a first message to a participant).
_REVIEW_BODY = {
    "Growth": ("*Growth review*\n"
               "1. Which option best supports new-user growth?\n"
               "2. Which agenda item must stay in the live meeting?\n"
               "3. Which items are already safe to treat as agreed?\n"
               "4. What assumption should I preserve in the brief?"),
    "Commerce": ("*Commerce review*\n"
                 "1. Which option best supports sale-window GMV?\n"
                 "2. Which agenda item must stay in the live meeting?\n"
                 "3. Which items are already safe to treat as agreed?\n"
                 "4. What assumption should I preserve in the brief?"),
    "Lead": ("*Lead / owner review*\n"
             "You're the meeting lead. What should the plan optimize for, and which agenda "
             "items must stay live vs. can be pre-agreed?"),
}


def _review_prompt(role: str) -> str:
    head = ("The meeting owner is prepping the Shopee SG 11.11 creator-mix decision and listed "
            f"you as *{role}*. Before I compress the agenda, I need your input.\n\n")
    return head + _REVIEW_BODY.get(role, "What's your take on the agenda?")


def _open_dm(client, user_id):
    return client.conversations_open(users=user_id)["channel"]["id"]


def _start_multihuman(initiator, session, roster, say, client):
    meeting = meeting_mod.Meeting(
        initiator=initiator,
        brief=session.get("inputs", {}).get("brief", ""),
        setup=session.get("inputs", {}).get("setup", ""),
        participants=roster,
    )
    _PENDING_MEETINGS[initiator] = meeting
    _USER_TO_MEETING[initiator] = initiator  # initiator routes here too (for compile/status)
    for pid in roster:
        _USER_TO_MEETING[pid] = initiator
    _MANUAL_SESSIONS.pop(initiator, None)  # intake done; switch to collecting

    roster_txt = ", ".join(f"<@{pid}> ({role})" for pid, role in roster.items())
    say(f"Reaching out to {roster_txt} for input. I'll compile the brief once everyone replies "
        "— or DM me `compile` to force it.")

    for pid, role in roster.items():
        prompt = _review_prompt(role)
        if pid == initiator:
            say(prompt)  # initiator is also a participant: ask them in this same DM
        else:
            client.chat_postMessage(channel=_open_dm(client, pid), text=prompt)


def _notify_progress(meeting, client):
    done, total = len(meeting.responses), len(meeting.participants)
    pend = meeting.pending()
    tail = (f" Waiting on {', '.join('<@'+u+'>' for u in pend)}." if pend else " Compiling now…")
    client.chat_postMessage(channel=_open_dm(client, meeting.initiator),
                            text=f":envelope_with_arrow: {done}/{total} responded.{tail}")


def _handle_meeting_dm(user, text, say, client):
    """Route a DM from a participant (or the initiator) of an in-flight meeting."""
    meeting = _PENDING_MEETINGS.get(_USER_TO_MEETING.get(user))
    if meeting is None or meeting.phase == "done":
        say("That meeting has already wrapped up.")
        return

    if user == meeting.initiator and text.strip().lower() in ("compile", "done"):
        _compile_and_post(meeting, client)
        return

    if user in meeting.participants and user not in meeting.responses:
        role = meeting.participants[user]
        ack = _ground_stance(meeting_mod.ROLE_TO_PERSONA[role], text)
        meeting.responses[user] = text
        say(ack or f"Got your {role} input — thanks.")
        _notify_progress(meeting, client)
        if meeting.all_responded():
            _compile_and_post(meeting, client)
        return

    pend = meeting.pending()
    if pend:
        say("Still waiting on " + ", ".join(f"<@{u}>" for u in pend)
            + ". DM me `compile` to force the brief now.")
    else:
        say("All input is in — compiling the brief now.")


def _compile_and_post(meeting, client):
    # Claim the compile atomically; the slow board build runs outside the lock.
    with _COMPILE_LOCK:
        if meeting.phase == "done":
            return
        meeting.phase = "done"
    owner_dm = _open_dm(client, meeting.initiator)
    client.chat_postMessage(channel=owner_dm, text="All input gathered — compiling the pre-meeting brief…")

    board = _build_board()
    text = f"Pre-meeting brief ready: {board.meeting_item_count()} items need the live meeting"
    blocks = render_blocks(board)
    try:
        if CHANNEL:
            app.client.chat_postMessage(channel=CHANNEL, blocks=blocks, text=text)
            client.chat_postMessage(channel=owner_dm, text="Posted the brief to the meeting channel.")
        else:
            client.chat_postMessage(channel=owner_dm, blocks=blocks, text=text)
    except SlackApiError as exc:
        if exc.response.get("error") != "not_in_channel":
            raise
        client.chat_postMessage(channel=owner_dm, blocks=blocks, text=text)

    for uid in list(meeting.participants) + [meeting.initiator]:
        _USER_TO_MEETING.pop(uid, None)
    _PENDING_MEETINGS.pop(meeting.initiator, None)


def _run_scripted_premeeting(respond, client):
    async def escalate(person, item_id, question):
        dm = client.conversations_open(users=HUMAN)
        client.chat_postMessage(channel=dm["channel"]["id"], text=f":mag: *{person} Agent*: {question}")
        # Demo: human's DM reply is handled by on_dm which updates the stance store.
        # For timing safety the orchestrator re-reads the store; we poll briefly.
        for _ in range(30):
            await asyncio.sleep(1)
            from pmle.stance_store import StanceStore
            s = StanceStore().get(person, item_id)
            if s and "client" in " ".join(s.key_assumptions).lower():
                return s.rationale
        return "no answer (timeout)"

    if _live_agents():
        board = asyncio.run(orchestrator.run_meeting(escalate=escalate))
    else:
        board = asyncio.run(orchestrator.run_meeting(
            escalate=escalate, ask_stance=_demo_ask_stance, classify_item=_demo_classify_item))
    text = f"Pre-meeting result: {board.meeting_item_count()} items need a meeting"
    blocks = render_blocks(board)
    try:
        client.chat_postMessage(channel=CHANNEL, blocks=blocks, text=text)
    except SlackApiError as exc:
        if exc.response.get("error") != "not_in_channel":
            raise
        respond(blocks=blocks, text=text)


# --- human DM -> hosted flow, multi-participant collection, or their persistent agent ---
@app.event("message")
def on_dm(event, say, client):
    if event.get("channel_type") != "im" or event.get("bot_id"):
        return
    user = event.get("user", "unknown")
    if user in _MANUAL_SESSIONS:
        _handle_manual_turn(user, event["text"], say, client)
        return
    if user in _USER_TO_MEETING:
        _handle_meeting_dm(user, event["text"], say, client)
        return
    agent, session = build_participant("John Taylor")  # demo: one human drives the meeting.
    result = asyncio.run(Runner.run(agent, event["text"], session=session))
    say(result.final_output)

# --- /premeeting starts the manual hosted flow ---
@app.command("/premeeting")
def on_premeeting(ack, respond, client, command):
    ack()
    user = command["user_id"]
    _MANUAL_SESSIONS[user] = manual_flow.new_session()
    dm = client.conversations_open(users=user)
    client.chat_postMessage(channel=dm["channel"]["id"], text=manual_flow.FIRST_PROMPT)
    respond(text="I opened a DM to host the pre-meeting setup.")


# --- /premeeting-compile force-compiles a multi-participant brief before everyone has replied ---
@app.command("/premeeting-compile")
def on_premeeting_compile(ack, respond, command, client):
    ack()
    meeting = _PENDING_MEETINGS.get(_USER_TO_MEETING.get(command["user_id"]))
    if meeting is None:
        respond("No pending meeting to compile.")
        return
    respond("Forcing brief compilation…")
    _compile_and_post(meeting, client)


# --- /premeeting-scripted runs the fast digest ---
@app.command("/premeeting-scripted")
def on_premeeting_scripted(ack, respond, client):
    ack("Spinning up the scripted pre-meeting orchestrator…")
    _run_scripted_premeeting(respond, client)

def main():
    if "SLACK_BOT_TOKEN" not in os.environ or "SLACK_APP_TOKEN" not in os.environ:
        raise RuntimeError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN are required to start Slack Socket Mode")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

if __name__ == "__main__":
    main()
