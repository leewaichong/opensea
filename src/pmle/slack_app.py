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

_FIRST_PROMPT = (
    "What meeting do you want to prepare?\n\n"
    "Tell me the decision you need the meeting to resolve, who should be involved, "
    "and what kind of agenda compression you want. A rough paragraph is enough."
)


def _next_manual_reply(user: str, text: str) -> str:
    session = _MANUAL_SESSIONS.setdefault(user, {"step": "brief", "answers": []})
    step = session["step"]
    session["answers"].append({"step": step, "text": text})

    if step == "brief":
        session["step"] = "setup"
        return (
            "Got it. I can host that pre-meeting.\n\n"
            "Please send the setup fields so I can collect the right stakeholder input:\n"
            "- meeting title\n"
            "- decision owner\n"
            "- participants and roles\n"
            "- known candidates/options\n"
            "- initial agenda\n"
            "- constraints or context\n\n"
            "For the Shopee demo, paste Turn 2 from `docs/demo-scenario-shopee.md`."
        )

    if step == "setup":
        session["step"] = "growth"
        return (
            "Thanks. I’ll collect stakeholder views before compressing the agenda.\n\n"
            "*Growth review prompt*\n"
            "Please review the draft agenda with a growth lens:\n"
            "1. Which option best supports new-user growth?\n"
            "2. Which agenda item must stay in the live meeting?\n"
            "3. Which items are already safe to treat as agreed?\n"
            "4. What assumption should I preserve in the brief?\n\n"
            "For the Shopee demo, paste Wai Chong’s Turn 3 answer."
        )

    if step == "growth":
        session["step"] = "commerce"
        return (
            "Growth input captured. I’m preserving the acquisition assumptions.\n\n"
            "*Commerce review prompt*\n"
            "Please review the draft agenda with a commerce lens:\n"
            "1. Which option best supports sale-window GMV?\n"
            "2. Which agenda item must stay in the live meeting?\n"
            "3. Which items are already safe to treat as agreed?\n"
            "4. What assumption should I preserve in the brief?\n\n"
            "For the Shopee demo, paste Shang’s Turn 4 answer."
        )

    if step == "commerce":
        session["step"] = "owner_gap"
        return (
            "Commerce input captured. I found a likely alignment gap.\n\n"
            "The stakeholders may agree on the same audience label, but optimize different outcomes: "
            "acquisition, GMV/conversion, or mainstream brand reach.\n\n"
            "From the decision-owner side, what should the plan optimize for? Or should the live agenda "
            "explicitly decide the split between those objectives?\n\n"
            "For the Shopee demo, paste John’s Turn 5 answer."
        )

    if step == "owner_gap":
        session["step"] = "confirm_growth"
        return (
            "Owner perspective captured. I’m moving resolved items into the pre-read.\n\n"
            "*Growth check:* are you comfortable moving deliverables, tracking, hero categories, "
            "and backup options into consensus? Any caveat I should preserve?\n\n"
            "For the Shopee demo, paste Wai Chong’s Turn 6 answer."
        )

    if step == "confirm_growth":
        session["step"] = "confirm_commerce"
        return (
            "Growth confirmation captured.\n\n"
            "*Commerce check:* are you comfortable moving deliverables, hero categories, and backup "
            "options into consensus? Any caveat I should preserve?\n\n"
            "For the Shopee demo, paste Shang’s Turn 6 answer."
        )

    session["step"] = "complete"
    return (
        "Pre-meeting inputs captured. I’m ready to generate the compressed brief.\n\n"
        "Run `/premeeting-scripted` for the Shopee demo digest, or keep sending refinements here "
        "if you want to adjust the brief first."
    )


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
    user = event.get("user", "unknown")
    if user in _MANUAL_SESSIONS:
        say(_next_manual_reply(user, event["text"]))
        return
    agent, session = build_participant("John Taylor")  # demo: one human drives the meeting.
    result = asyncio.run(Runner.run(agent, event["text"], session=session))
    say(result.final_output)

# --- /premeeting starts the manual hosted flow ---
@app.command("/premeeting")
def on_premeeting(ack, respond, client, command):
    ack()
    user = command["user_id"]
    _MANUAL_SESSIONS[user] = {"step": "brief", "answers": []}
    dm = client.conversations_open(users=user)
    client.chat_postMessage(channel=dm["channel"]["id"], text=_FIRST_PROMPT)
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
