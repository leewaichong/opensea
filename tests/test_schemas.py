from pmle.schemas import Stance, ClassificationResult, ActionItem, AgendaItem, BoardState


def test_stance_roundtrips():
    s = Stance(
        stakeholder="Security",
        item_id="security-token-path",
        position="agree_with_condition",
        rationale="Ship only if no client-side token.",
        key_assumptions=["No client-side token storage"],
        confidence=0.86,
        evidence_refs=["kb-sec-2025"],
    )
    assert Stance.model_validate_json(s.model_dump_json()) == s


def test_classification_status_constrained():
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ClassificationResult(item_id="x", status="banana", summary="", divergence=None,
                             cited_stances=[], follow_up=None)


def test_board_counts_meeting_items():
    board = BoardState(
        decision="ship?", owner="PM",
        items=[
            ClassificationResult(item_id="a", status="agreed", summary="", divergence=None, cited_stances=[], follow_up=None),
            ClassificationResult(item_id="b", status="crux", summary="", divergence=None, cited_stances=[], follow_up=None),
            ClassificationResult(item_id="c", status="fake_agreement", summary="", divergence="x", cited_stances=[], follow_up=None),
        ],
        action_items=[],
    )
    assert board.meeting_item_count() == 2  # crux + fake_agreement
