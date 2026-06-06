"""The brief must show everything: the items that still need the live meeting AND the
async-resolved consensus (agreed agenda items + resolved action items), per the demo
sample. Earlier the renderer hid all non-crux items behind a "3 resolved" count."""
from pmle.digest import render_blocks, render_text
from pmle.schemas import BoardState, ClassificationResult, ActionItem


def _board():
    return BoardState(
        decision="Decide the 11.11 creator mix.",
        owner="John Taylor",
        items=[
            ClassificationResult(item_id="role-mix", status="crux",
                                 summary="Hero vs conversion split unresolved.",
                                 divergence="Wai Chong: Mika; Shang: Jayden."),
            ClassificationResult(item_id="deliverables", status="agreed",
                                 summary="No blocking divergence found."),
            ClassificationResult(item_id="tracking", status="agreed",
                                 summary="No blocking divergence found."),
        ],
        action_items=[
            ActionItem(id="ai-live-slot", status="resolved",
                       text="Confirm a Shopee Live slot",
                       resolution="At least one Shopee Live slot is required.",
                       resolved_by=["Shang"]),
        ],
    )


def test_blocks_show_both_discussion_and_resolved():
    blocks = render_blocks(_board())
    blob = str(blocks)
    # The live-meeting item is present...
    assert "role-mix" in blob and "Needs the live meeting" in blob
    # ...AND the resolved consensus is no longer hidden behind a count.
    assert "Already aligned" in blob
    assert "deliverables" in blob and "tracking" in blob          # agreed agenda items shown
    assert "At least one Shopee Live slot is required." in blob   # resolved action item shown
    assert "Shang" in blob                                        # who cleared it


def test_agreed_items_use_agenda_text_not_generic_summary():
    # An agreed item known in the agenda renders its descriptive text, not "No blocking..."
    blob = str(render_blocks(_board()))
    assert "Confirm deliverables" in blob


def test_header_count_matches_footer_and_clarify_is_separate():
    # needs_clarification must NOT inflate the "needs the meeting" count: header (crux+fake),
    # the footer's "for the meeting", and the section must all agree, with 🔵 items in their
    # own "Needs more input" bucket.
    board = BoardState(
        decision="d", owner="o",
        items=[
            ClassificationResult(item_id="a", status="crux", summary="conflict"),
            ClassificationResult(item_id="b", status="fake_agreement", summary="fake"),
            ClassificationResult(item_id="c", status="needs_clarification", summary="one side only"),
            ClassificationResult(item_id="e", status="needs_clarification", summary="thin"),
            ClassificationResult(item_id="f", status="agreed", summary="aligned"),
        ],
    )
    assert board.meeting_item_count() == 2                 # header counts crux+fake only
    blob = str(render_blocks(board))
    assert "Pre-meeting: 5 → 2 items" in blob
    assert "2 for the meeting" in blob                     # footer agrees with header
    assert "2 need more input" in blob                     # 🔵 items broken out separately
    assert "Needs more input" in blob


def test_text_render_includes_consensus_section():
    txt = render_text(_board())
    assert "Needs the live meeting:" in txt
    assert "Already aligned — skip in the meeting:" in txt
    assert "At least one Shopee Live slot is required." in txt
