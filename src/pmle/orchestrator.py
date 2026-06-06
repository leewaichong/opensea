from pmle.schemas import BoardState, ClassificationResult, ActionItem
from pmle.crux_engine import classify_item
from pmle.participants import ask_stance
from pmle.data.agenda import DECISION, OWNER, AGENDA, ACTION_ITEMS, PARTICIPANTS


async def run_meeting(escalate=None) -> BoardState:
    """Transient orchestrator pass. `escalate(person, item_id, question) -> str` is the
    Slack-DM hook for needs_clarification; None disables escalation (pure async demo)."""
    results: list[ClassificationResult] = []
    for item in AGENDA:
        stances = [await ask_stance(p, item.id, item.text) for p in PARTICIPANTS]
        result = await classify_item(stances)
        if result.status == "needs_clarification" and escalate is not None:
            answer = await escalate("Security", item.id, result.follow_up or "Clarify?")
            # human answered -> re-read updated stance and re-classify
            stances = [await ask_stance(p, item.id, item.text) for p in PARTICIPANTS]
            result = await classify_item(stances)
            result.summary += f" (resolved via human: {answer})"
        results.append(result)

    action_items = await _clear_action_items()
    return BoardState(decision=DECISION, owner=OWNER, items=results, action_items=action_items)


async def _clear_action_items() -> list[ActionItem]:
    # For the demo, deterministically pre-clear the Shopee pre-read items.
    cleared = []
    for ai in ACTION_ITEMS:
        if ai.id == "ai-live-slot":
            cleared.append(ai.model_copy(update={
                "status": "resolved", "owner": "Shang",
                "resolution": "At least one Shopee Live slot is required.", "resolved_by": ["Shang"]}))
        elif ai.id == "ai-tracking":
            cleared.append(ai.model_copy(update={
                "status": "resolved",
                "resolution": "Track affiliate links, promo codes, voucher redemption, live GMV, and app installs.",
                "resolved_by": ["Wai Chong", "Shang"]}))
        else:
            cleared.append(ai.model_copy(update={
                "status": "resolved",
                "resolution": "Brand-safety, disclosure, and competitor-sponsorship review required.",
                "resolved_by": ["John Taylor", "Shang"]}))
    return cleared
