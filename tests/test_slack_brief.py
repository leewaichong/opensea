"""Lock down which brief path /premeeting takes per mode.

This is the one assertion that separates "wired correctly" from "the canned demo path
silently leaked into the live path." We can't exercise the live LLM grounding offline, so
these tests only verify the dispatch, not the grounding itself.
"""
import pmle.slack_app as slack_app
from pmle import orchestrator
from pmle.schemas import BoardState


def _stub_run_meeting(captured):
    async def fake_run_meeting(escalate=None, ask_stance=None, classify_item=None):
        captured["ask_stance"] = ask_stance
        captured["classify_item"] = classify_item
        return BoardState(decision="d", owner="o", items=[], action_items=[])
    return fake_run_meeting


def test_live_mode_grounds_via_module_level_functions(monkeypatch):
    monkeypatch.setenv("PMLE_LIVE_AGENTS", "1")
    captured = {}
    monkeypatch.setattr(orchestrator, "run_meeting", _stub_run_meeting(captured))
    slack_app._build_board()
    # No overrides -> run_meeting reads the grounded stances + live classifier.
    assert captured["ask_stance"] is None
    assert captured["classify_item"] is None


def test_default_mode_uses_deterministic_demo_path(monkeypatch):
    monkeypatch.delenv("PMLE_LIVE_AGENTS", raising=False)
    captured = {}
    monkeypatch.setattr(orchestrator, "run_meeting", _stub_run_meeting(captured))
    slack_app._build_board()
    # Canned, input-independent digest -> demo stubs are injected explicitly.
    assert captured["ask_stance"] is slack_app._demo_ask_stance
    assert captured["classify_item"] is slack_app._demo_classify_item
