from pmle.manual_flow import (
    advance_manual_flow,
    missing_setup_fields,
    new_session,
)

_FULL_SETUP = (
    "Meeting title: Shopee SG 11.11 Creator Mix Planning. "
    "Participants: Wai Chong (Growth), Shang (Commerce), John Taylor (Lead). "
    "Initial agenda: align objective, decide role mix, choose creators..."
)


def test_new_session_starts_at_brief():
    s = new_session()
    assert s == {"step": "brief", "inputs": {}}


def test_full_flow_collects_inputs_grounds_and_completes():
    s = new_session()

    out = advance_manual_flow(s, "Prep a decision meeting for the 11.11 creator campaign.")
    assert s["step"] == "setup"
    assert out["ground"] is None and out["complete"] is False

    out = advance_manual_flow(s, _FULL_SETUP)
    assert s["step"] == "growth"  # setup complete -> advance
    assert out["ground"] is None

    out = advance_manual_flow(s, "Growth: optimize new-user acquisition; prefer Mika as hero.")
    assert out["ground"] == ("Wai Chong", "Growth: optimize new-user acquisition; prefer Mika as hero.")
    assert s["step"] == "commerce"

    out = advance_manual_flow(s, "Commerce: optimize GMV; need Jayden for Shopee Live conversion.")
    assert out["ground"] == ("Shang", "Commerce: optimize GMV; need Jayden for Shopee Live conversion.")
    assert s["step"] == "owner_gap"

    out = advance_manual_flow(s, "Owner: mainstream-safe youth reach; Mika or Nora as hero.")
    assert out["ground"] == ("John Taylor", "Owner: mainstream-safe youth reach; Mika or Nora as hero.")
    assert s["step"] == "confirm_growth"

    out = advance_manual_flow(s, "Growth confirms, preserve paid amplification.")
    assert out["ground"] is None and out["complete"] is False
    assert s["step"] == "confirm_commerce"

    out = advance_manual_flow(s, "Commerce confirms, require one Shopee Live slot.")
    assert out["complete"] is True
    assert s["step"] == "complete"

    # All seven inputs are retained in structured session state.
    assert set(s["inputs"]) == {
        "brief", "setup", "growth", "commerce",
        "owner_gap", "confirm_growth", "confirm_commerce",
    }


def test_setup_reasks_when_fields_missing_without_advancing():
    s = new_session()
    advance_manual_flow(s, "I want to prep a meeting.")  # -> setup
    out = advance_manual_flow(s, "It's about the 11.11 campaign.")  # no title/participants/agenda
    assert s["step"] == "setup"  # stayed put
    assert out["ground"] is None and out["complete"] is False
    assert s["inputs"]["setup"] == "It's about the 11.11 campaign."


def test_missing_setup_fields_detection():
    assert missing_setup_fields(_FULL_SETUP) == []
    assert set(missing_setup_fields("just some context")) == {
        "meeting title", "participants", "agenda"
    }
