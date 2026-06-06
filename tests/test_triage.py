"""Triage: demo-mode intent heuristic + the LLM roster reader's parse/validation layer."""
import asyncio

import agents

import pmle.triage as t


def test_heuristic_fires_on_prep_language():
    assert t.heuristic_intent("help me prep the 11.11 creator mix meeting")
    assert t.heuristic_intent("can you prepare a pre-meeting for friday")
    assert t.heuristic_intent("what's the agenda for the launch?")
    assert t.heuristic_intent("PRE MEETING please")  # hyphen/space + case tolerated


def test_heuristic_ignores_chitchat():
    assert not t.heuristic_intent("hey how's it going")
    assert not t.heuristic_intent("let's meet for lunch")
    # ambient words that are NOT prep intent must not spin up a meeting
    assert not t.heuristic_intent("can you sync the files and decide later")
    assert not t.heuristic_intent("")


def _fake_runner(output):
    class _Result:
        final_output = output

    class _FakeRunner:
        @staticmethod
        async def run(agent, prompt):
            return _Result()
    return _FakeRunner


def test_llm_roster_keeps_only_valid_ids_and_roles(monkeypatch):
    # Model returns an id outside the target list and an invalid role — both must be dropped,
    # so a hallucinated entry can never leak into the meeting.
    monkeypatch.setattr(
        agents, "Runner",
        _fake_runner('{"U_WC":"Growth","U_SH":"Commerce","U_BAD":"Growth","U_JT":"Wizard"}'))
    out = asyncio.run(t.llm_roster("msg", ["U_WC", "U_SH", "U_JT"]))
    assert out == {"U_WC": "Growth", "U_SH": "Commerce"}


def test_llm_roster_tolerates_fenced_json(monkeypatch):
    monkeypatch.setattr(agents, "Runner",
                        _fake_runner('```json\n{"U_WC":"Lead"}\n```'))
    assert asyncio.run(t.llm_roster("msg", ["U_WC"])) == {"U_WC": "Lead"}


def test_llm_roster_bad_json_is_empty(monkeypatch):
    monkeypatch.setattr(agents, "Runner", _fake_runner("sorry, not sure"))
    assert asyncio.run(t.llm_roster("msg", ["U_WC"])) == {}
