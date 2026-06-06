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
    # For the demo, deterministically pre-clear the resolvable ones; leave one needing an owner.
    cleared = []
    for ai in ACTION_ITEMS:
        if ai.id == "ai-rollback":
            cleared.append(ai.model_copy(update={
                "status": "resolved", "owner": "SRE",
                "resolution": "SRE accepted rollback ownership.", "resolved_by": ["Backend", "SRE"]}))
        elif ai.id == "ai-loadtest":
            cleared.append(ai.model_copy(update={
                "status": "needs_owner",
                "resolution": "No agent could schedule it without SRE sign-off."}))
        else:
            cleared.append(ai.model_copy(update={
                "status": "resolved", "resolution": "Confirmed by the owning agent."}))
    return cleared
