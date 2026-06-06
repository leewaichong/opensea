import pytest
from pmle import orchestrator
from pmle.schemas import ClassificationResult


@pytest.mark.asyncio
async def test_nine_to_two(monkeypatch):
    # Deterministic classifier: objective -> fake_agreement, role-mix -> crux, rest -> agreed.
    async def fake_classify(stances):
        item = stances[0].item_id
        if item == "objective":
            return ClassificationResult(item_id=item, status="fake_agreement",
                summary="same words diff assumptions", divergence="younger shoppers means different outcomes",
                cited_stances=["Wai Chong", "Shang", "John Taylor"])
        if item == "role-mix":
            return ClassificationResult(item_id=item, status="crux", summary="creator role split")
        return ClassificationResult(item_id=item, status="agreed", summary="ok")

    async def fake_ask(person, item_id, item_text):
        from pmle.schemas import Stance
        return Stance(stakeholder=person, item_id=item_id, position="support", rationale="r")

    monkeypatch.setattr(orchestrator, "classify_item", fake_classify)
    monkeypatch.setattr(orchestrator, "ask_stance", fake_ask)

    board = await orchestrator.run_meeting()
    assert board.meeting_item_count() == 2
    statuses = {i.item_id: i.status for i in board.items}
    assert statuses["objective"] == "fake_agreement"
    assert statuses["role-mix"] == "crux"
    assert all(a.status == "resolved" for a in board.action_items)
