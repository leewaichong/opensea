import pytest
from pmle import orchestrator
from pmle.schemas import ClassificationResult


@pytest.mark.asyncio
async def test_nine_to_two(monkeypatch):
    # Deterministic classifier: security -> fake_agreement, load -> crux, rest -> agreed.
    async def fake_classify(stances):
        item = stances[0].item_id
        if item == "security":
            return ClassificationResult(item_id=item, status="fake_agreement",
                summary="same words diff assumptions", divergence="server-session vs no-token",
                cited_stances=["PM", "Security"])
        if item == "load":
            return ClassificationResult(item_id=item, status="crux", summary="load risk")
        return ClassificationResult(item_id=item, status="agreed", summary="ok")

    async def fake_ask(person, item_id, item_text):
        from pmle.schemas import Stance
        return Stance(stakeholder=person, item_id=item_id, position="support", rationale="r")

    monkeypatch.setattr(orchestrator, "classify_item", fake_classify)
    monkeypatch.setattr(orchestrator, "ask_stance", fake_ask)

    board = await orchestrator.run_meeting()
    assert board.meeting_item_count() == 2
    statuses = {i.item_id: i.status for i in board.items}
    assert statuses["security"] == "fake_agreement"
    assert statuses["load"] == "crux"
    assert any(a.status == "needs_owner" for a in board.action_items)
