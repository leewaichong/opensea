# Slack app manifest:
# Socket Mode ON; bot scopes chat:write, im:write, im:history, commands,
# app_mentions:read; slash commands /premeeting and /premeeting-scripted;
# subscribe to message.im.
#
# Brief generation has two modes, gated on PMLE_LIVE_AGENTS:
#   default (unset/0): /premeeting collects the user's answers but the final brief is the
#                      deterministic cached Shopee digest (same output as /premeeting-scripted)
#                      — input-independent, safe for stage timing.
#   PMLE_LIVE_AGENTS=1: each stakeholder reply is grounded into that participant's Stance via
#                      their persistent agent, and the brief is classified live from the
#                      grounded stances. This is the only mode where the brief reflects what
#                      the user actually typed. Requires OPENAI_API_KEY; ~21 extra agent calls.
import os, asyncio
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from pmle import manual_flow, orchestrator
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


def _handle_manual_turn(user, text, say):
    """Drive one DM turn of the hosted /premeeting flow."""
    session = _MANUAL_SESSIONS[user]
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


# --- human DM -> their persistent agent (conversational contract editing) ---
@app.event("message")
def on_dm(event, say):
    if event.get("channel_type") != "im" or event.get("bot_id"):
        return
    user = event.get("user", "unknown")
    if user in _MANUAL_SESSIONS:
        _handle_manual_turn(user, event["text"], say)
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
