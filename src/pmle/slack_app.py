# Slack app manifest:
# Socket Mode ON; bot scopes chat:write, im:write, im:history, commands,
# app_mentions:read; slash command /premeeting; subscribe to message.im.
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
    if item == "security":
        return ClassificationResult(
            item_id=item,
            status="fake_agreement",
            summary="All agree on secure checkout, but assumptions differ.",
            divergence="PM/Backend: server-side session; Security: no client-side token storage",
            cited_stances=["PM", "Backend", "Security"],
            follow_up="Confirm whether any checkout token is stored client-side.",
        )
    if any(s.position == "block" for s in stances):
        return ClassificationResult(
            item_id=item,
            status="crux",
            summary="SRE blocks until 11.11 load readiness is proven.",
            divergence="SRE needs traffic simulation before launch.",
            cited_stances=["SRE", "PM"],
        )
    return ClassificationResult(
        item_id=item,
        status="agreed",
        summary="No blocking divergence found.",
        cited_stances=[s.stakeholder for s in stances],
    )

# --- human DM -> their persistent agent (conversational contract editing) ---
@app.event("message")
def on_dm(event, say):
    if event.get("channel_type") != "im" or event.get("bot_id"):
        return
    agent, session = build_participant("Security")  # demo: the one human is Security
    result = asyncio.run(Runner.run(agent, event["text"], session=session))
    say(result.final_output)

# --- /premeeting kicks off the orchestrator ---
@app.command("/premeeting")
def on_premeeting(ack, respond, client):
    ack("Spinning up the pre-meeting orchestrator…")
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

def main():
    if "SLACK_BOT_TOKEN" not in os.environ or "SLACK_APP_TOKEN" not in os.environ:
        raise RuntimeError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN are required to start Slack Socket Mode")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

if __name__ == "__main__":
    main()
