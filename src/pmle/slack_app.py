# Slack app manifest:
# Socket Mode ON; bot scopes chat:write, im:write, im:history, commands,
# app_mentions:read; slash commands /premeeting and /premeeting-scripted;
# subscribe to message.im.
import os, asyncio
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError
from pmle import orchestrator
from pmle.data.cached_stances import CACHED
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

_MANUAL_BLOCKS = [
    {"type": "header", "text": {"type": "plain_text", "text": "Manual Pre-Meeting Script"}},
    {"type": "section", "text": {"type": "mrkdwn", "text": (
        "*Turn 1: John starts*\n"
        "```I need to prep a decision meeting for Shopee SG's 11.11 creator campaign.\n\n"
        "We need to decide the creator mix for the sale: who should be the hero face, "
        "who should drive Shopee Live conversion, and what criteria we should use to make that split. "
        "I want the meeting to be short and focused, so please collect input from the key stakeholders "
        "first and generate the final agenda.```"
    )}},
    {"type": "section", "text": {"type": "mrkdwn", "text": (
        "*Bot asks John for missing setup fields:*\n"
        "meeting title, participants and roles, initial agenda, known candidates, constraints/context."
    )}},
    {"type": "section", "text": {"type": "mrkdwn", "text": (
        "*Manual stakeholder inputs to paste next:*\n"
        "1. John provides meeting details from `docs/demo-scenario-shopee.md` Turn 2.\n"
        "2. Wai Chong gives Growth input from Turn 3.\n"
        "3. Shang gives Commerce input from Turn 4.\n"
        "4. Bot asks John about the alignment gap from Turn 5.\n"
        "5. Wai Chong and Shang confirm compressed agenda from Turn 6."
    )}},
    {"type": "section", "text": {"type": "mrkdwn", "text": (
        "When you want the generated digest, run `/premeeting-scripted`. "
        "That command uses the same Shopee user stories and returns the `9 → 2` brief."
    )}},
]


def _run_scripted_premeeting(respond, client):
    if os.environ.get("PMLE_LIVE_AGENTS") != "1":
        orchestrator.ask_stance = _demo_ask_stance
        orchestrator.classify_item = _demo_classify_item

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

    board = asyncio.run(orchestrator.run_meeting(escalate=escalate))
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
    agent, session = build_participant("John Taylor")  # demo: one human drives the meeting.
    result = asyncio.run(Runner.run(agent, event["text"], session=session))
    say(result.final_output)

# --- /premeeting starts the manual script ---
@app.command("/premeeting")
def on_premeeting(ack, respond):
    ack()
    respond(blocks=_MANUAL_BLOCKS, text="Manual pre-meeting script ready.")


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
