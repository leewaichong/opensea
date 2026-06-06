# Slack app manifest:
# Socket Mode ON; bot scopes chat:write, im:write, im:history, commands,
# app_mentions:read; slash command /premeeting; subscribe to message.im.
import os, asyncio
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from pmle import orchestrator
from pmle.participants import build_participant
from agents import Runner
from pmle.digest import render_blocks

load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN", "xoxb-import-smoke"),
          token_verification_enabled=False)
HUMAN = os.environ.get("PMLE_HUMAN_USER")
CHANNEL = os.environ.get("PMLE_MEETING_CHANNEL")

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

    async def escalate(person, item_id, question):
        client.chat_postMessage(channel=HUMAN, text=f":mag: *{person} Agent*: {question}")
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
    client.chat_postMessage(channel=CHANNEL, blocks=render_blocks(board),
                            text=f"Pre-meeting result: {board.meeting_item_count()} items need a meeting")

def main():
    if "SLACK_BOT_TOKEN" not in os.environ or "SLACK_APP_TOKEN" not in os.environ:
        raise RuntimeError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN are required to start Slack Socket Mode")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

if __name__ == "__main__":
    main()
