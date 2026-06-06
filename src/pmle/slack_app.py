# Slack app manifest:
# Socket Mode ON; bot scopes chat:write, im:write, im:history, commands,
# app_mentions:read; slash commands /premeeting, /premeeting-compile, /premeeting-scripted,
# /clear; subscribe to message.im.
#
# KILL SWITCH: typing `clear` / `reset` / `restart` in the DM (or running /clear) wipes the
# user's flow state and resets the scenario to the seeded baseline — escapes any state.
# If the user @mentions teammates but no role can be inferred for them (or they can't be
# DM'd), the bot ASKS to clarify instead of silently self-interviewing the sender.
#
# ENTRY POINT: free-form DM. There's no slash command to start — the user just talks to the
# bot ("help me prep the 11.11 creator-mix meeting; <@U_SHANG> owns the sale-window numbers,
# <@U_JT> is running the call, I'll cover acquisition") and the bot deduces the intent
# (triage.py) and spins the flow up itself:
#   - @mentioned teammates present  -> one-shot: infer each role from the text (live: LLM;
#                                      demo: keyword) and DM each teammate for input.
#   - prep intent but no mentions   -> ask the one setup question, then fan out.
#   - not a meeting request         -> the user's persistent agent answers (chat).
# It grounds each reply into that role's persona Stance and auto-compiles once everyone has
# replied (or the initiator DMs `compile`). The compiled brief is DM'd to every participant
# (and the initiator) — there is no meeting channel. /premeeting still works as a manual
# fallback entry; /premeeting-scripted is the fast cached path.
#
# Brief generation has two modes, gated on PMLE_LIVE_AGENTS:
#   default (unset/0): intent is keyword-detected (offline) and the final brief is the
#                      deterministic cached Shopee digest (same output as /premeeting-scripted)
#                      — input-independent, safe for stage timing.
#   PMLE_LIVE_AGENTS=1: intent is classified by the router agent, each stakeholder reply is
#                      grounded into that participant's Stance via their persistent agent, and
#                      the brief is classified live from the grounded stances. This is the only
#                      mode where the brief reflects what the user actually typed. Requires
#                      OPENAI_API_KEY; ~21 extra agent calls.
import os, asyncio, threading
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from pmle import manual_flow, meeting as meeting_mod, orchestrator, triage
from pmle.data.cached_stances import CACHED
from pmle.data.agenda import AGENDA
from pmle.data.personas import PERSONAS
from pmle.participants import build_participant
from pmle.stance_store import StanceStore
from pmle.schemas import ClassificationResult, Stance
from agents import Runner
from pmle.digest import render_blocks

load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN", "xoxb-import-smoke"),
          token_verification_enabled=False)
HUMAN = os.environ.get("PMLE_HUMAN_USER")
_CACHE = {(s.stakeholder, s.item_id): s for s in CACHED}
_MANUAL_SESSIONS: dict[str, dict] = {}
# Multi-participant meetings, keyed by initiator user id. _USER_TO_MEETING routes any
# participant's (or the initiator's) DM back to the meeting they belong to.
_PENDING_MEETINGS: dict[str, "meeting_mod.Meeting"] = {}
_USER_TO_MEETING: dict[str, str] = {}
# Serializes the compile trigger so concurrent participant replies can't double-post the brief.
_COMPILE_LOCK = threading.Lock()

# Kill switch: typing any of these (or running /clear) wipes the user's flow and resets the
# scenario back to the seeded baseline — "start from the very beginning".
_RESET_WORDS = {"clear", "reset", "restart"}


def _reset_flow_state(user: str) -> list[str]:
    """Drop all in-flight flow state for `user`. If they own a meeting, tear down its routing
    for every participant too. Pure in-memory; safe to call any time."""
    cleared = []
    if _MANUAL_SESSIONS.pop(user, None) is not None:
        cleared.append("setup session")
    owned = _PENDING_MEETINGS.pop(user, None)
    if owned is not None:
        for pid in list(owned.participants) + [owned.initiator]:
            _USER_TO_MEETING.pop(pid, None)
        cleared.append("pending meeting")
    elif _USER_TO_MEETING.pop(user, None) is not None:
        cleared.append("meeting link")
    return cleared


def _reset_scenario() -> None:
    """Reset shared agent memory to the seeded baseline: clear each persona's persistent
    session (so grounding starts clean) and re-seed the stance store. Mochi itself is a
    stateless classifier, so there's nothing to kill there — this is the rest of 'start over'."""
    store = StanceStore()
    for s in CACHED:
        store.set(s.stakeholder, s)
    for person in PERSONAS:
        _, session = build_participant(person)
        try:
            asyncio.run(session.clear_session())
        except Exception:
            pass  # best-effort; a locked/empty session must not break the reset


def _full_reset(user: str) -> list[str]:
    cleared = _reset_flow_state(user)
    _reset_scenario()
    return cleared


def _cant_place_roles(unresolved: list[str]) -> str:
    """Shown when the user tagged people but we couldn't infer a role for any of them — so we
    ask instead of silently self-interviewing the sender through every role."""
    who = ", ".join(f"<@{u}>" for u in unresolved) or "the people you tagged"
    return (f"I see you tagged {who}, but I couldn't tell what role each should play. "
            "Re-send them with a role each — e.g. `<@U…> growth`, `<@U…> commerce`, "
            "`<@U…> lead` — or describe what each person owns and I'll infer it. "
            "(Type `clear` to start over.)")


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


def _detect_intent(text: str) -> bool:
    """Deduce whether a free-form DM is a request to prep a meeting. Live mode asks the
    router agent; demo mode uses the offline keyword heuristic."""
    if _live_agents():
        return asyncio.run(triage.llm_intent(text))
    return triage.heuristic_intent(text)


def _extract_roster(text: str, user: str) -> dict:
    """Map @mentioned teammates to roles. Live mode infers each role from the free-form text
    (an LLM read of what the person owns); demo mode keyword-matches deterministically."""
    if _live_agents():
        targets = meeting_mod.extract_targets(text, initiator=user)
        if not targets:
            return {}
        return asyncio.run(triage.llm_roster(text, targets))
    return meeting_mod.parse_participants(text, initiator=user)


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
    """Deliver the digest on the current surface (DM `say` or slash `respond`). Used by the
    solo flow, where the initiator voices every role and is the only recipient."""
    text = f"Pre-meeting brief ready: {board.meeting_item_count()} items need the live meeting"
    blocks = render_blocks(board)
    (say or respond)(text=text, blocks=blocks)


def _handle_manual_turn(user, text, say, client):
    """Drive one DM turn of the hosted /premeeting flow.

    At the setup step, if the initiator @mentioned real participants, branch into the
    multi-participant flow (DM each of them); otherwise stay solo (initiator voices all)."""
    session = _MANUAL_SESSIONS[user]

    if session.get("step") == "setup":
        targets = meeting_mod.extract_targets(text, initiator=user)
        roster = _extract_roster(text, user)
        if [p for p in roster if p != user]:           # at least one real teammate placed
            session.setdefault("inputs", {})["setup"] = text
            _start_multihuman(user, session, roster, say, client,
                              unplaced=[t for t in targets if t not in roster])
            return
        if targets:                                    # tagged people but couldn't place them
            say(text=_cant_place_roles([t for t in targets if t not in roster]))
            return                                     # stay in setup for a retry, do NOT solo

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


def _start_multihuman(initiator, session, roster, say, client, unplaced=None):
    # Open DMs up front and drop anyone we can't reach, so the meeting never waits on a ghost
    # participant (which would otherwise block auto-compile forever).
    reachable, unreachable, dm_channel = {}, [], {}
    for pid, role in roster.items():
        if pid == initiator:
            reachable[pid] = role
            continue
        try:
            dm_channel[pid] = _open_dm(client, pid)
            reachable[pid] = role
        except SlackApiError:
            unreachable.append(pid)

    if not [p for p in reachable if p != initiator]:
        # Nobody to coordinate with — abort cleanly instead of creating a stuck meeting.
        who = ", ".join(f"<@{u}>" for u in unreachable) or "the people you tagged"
        say(f"I couldn't message {who} — they may not be in this workspace or haven't allowed "
            "DMs from me. Re-tag reachable teammates, or DM me their input yourself. "
            "(Type `clear` to start over.)")
        return

    meeting = meeting_mod.Meeting(
        initiator=initiator,
        brief=session.get("inputs", {}).get("brief", ""),
        setup=session.get("inputs", {}).get("setup", ""),
        participants=reachable,
    )
    _PENDING_MEETINGS[initiator] = meeting
    _USER_TO_MEETING[initiator] = initiator  # initiator routes here too (for compile/status)
    for pid in reachable:
        _USER_TO_MEETING[pid] = initiator
    _MANUAL_SESSIONS.pop(initiator, None)  # intake done; switch to collecting

    # Surface anyone tagged but left out — couldn't infer a role (unplaced) or couldn't DM
    # (unreachable) — so they never just vanish. The meeting proceeds with whoever we have.
    left_out = list(unplaced or []) + unreachable
    roster_txt = ", ".join(f"<@{pid}> ({role})" for pid, role in reachable.items())
    miss = (f" Couldn't include {', '.join('<@'+u+'>' for u in left_out)} — re-tag them with a "
            "role to add them." if left_out else "")
    say(f"Reaching out to {roster_txt} for input. I'll compile the brief once everyone "
        f"replies — or DM me `compile` to force it.{miss}")

    for pid, role in reachable.items():
        prompt = _review_prompt(role)
        if pid == initiator:
            say(prompt)  # initiator is also a participant: ask them in this same DM
        else:
            client.chat_postMessage(channel=dm_channel[pid], text=prompt)


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

    # No channel: DM the compiled brief to every participant (and the initiator). Dedupe so
    # an initiator who joined as a participant (`me Growth`) isn't messaged twice.
    recipients = set(meeting.participants) | {meeting.initiator}
    for uid in recipients:
        client.chat_postMessage(channel=_open_dm(client, uid), blocks=blocks, text=text)
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
    respond(blocks=blocks, text=text)


# --- human DM is the only entry point: route an in-flight conversation, else deduce intent ---
@app.event("message")
def on_dm(event, say, client):
    if event.get("channel_type") != "im" or event.get("bot_id"):
        return
    user = event.get("user", "unknown")
    text = event.get("text", "")

    # Kill switch first — escapes any state, even mid-meeting.
    if text.strip().lower() in _RESET_WORDS:
        _full_reset(user)
        say(text=":broom: Cleared — back to the very beginning. Tell me what meeting to prep "
                 "and tag who's involved.")
        return

    # Already mid-conversation: continue where they are.
    if user in _MANUAL_SESSIONS:
        _handle_manual_turn(user, text, say, client)
        return
    if user in _USER_TO_MEETING:
        _handle_meeting_dm(user, text, say, client)
        return

    # Fresh DM. @mentioned teammates make this self-evidently a meeting setup, so spin the
    # multi-participant flow up one-shot (live mode infers each role from the text).
    targets = meeting_mod.extract_targets(text, initiator=user)
    roster = _extract_roster(text, user)
    if [p for p in roster if p != user]:               # at least one real teammate placed
        _start_multihuman(user, {"inputs": {"brief": text, "setup": text}}, roster, say, client,
                          unplaced=[t for t in targets if t not in roster])
        return
    if targets:
        # Tagged people but couldn't place any in a role — ask to clarify; do NOT self-interview
        # the sender. Open a setup session so the corrected re-tag routes back here.
        _MANUAL_SESSIONS[user] = {"step": "setup", "inputs": {"brief": text}}
        say(text=_cant_place_roles([t for t in targets if t not in roster]))
        return
    if _detect_intent(text):
        # Meeting intent but no one tagged — drop into setup and ask the one question.
        _MANUAL_SESSIONS[user] = {"step": "setup", "inputs": {"brief": text}}
        say(text=manual_flow.SETUP_PROMPT)
        return

    # Not a meeting request — the user's persistent agent answers (also grounds the human's
    # reply into the stance store during /premeeting-scripted escalation).
    agent, session = build_participant("John Taylor")
    result = asyncio.run(Runner.run(agent, text, session=session))
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


# --- /clear kill switch: wipe the user's flow + reset the scenario to baseline ---
@app.command("/clear")
def on_clear(ack, respond, command):
    ack()
    _full_reset(command["user_id"])
    respond(text=":broom: Cleared — back to the very beginning. DM me what meeting to prep "
                 "and tag who's involved.")

def main():
    if "SLACK_BOT_TOKEN" not in os.environ or "SLACK_APP_TOKEN" not in os.environ:
        raise RuntimeError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN are required to start Slack Socket Mode")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

if __name__ == "__main__":
    main()
