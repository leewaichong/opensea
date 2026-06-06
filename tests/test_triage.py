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


def test_llm_roster_open_roles_keeps_free_text_labels(monkeypatch):
    # Dynamic mode: any short label is valid, but ids outside the target set are still dropped.
    monkeypatch.setattr(agents, "Runner",
                        _fake_runner('{"U_FIN":"Finance","U_ENG":"Engineering","U_BAD":"Legal"}'))
    out = asyncio.run(t.llm_roster("msg", ["U_FIN", "U_ENG"], open_roles=True))
    assert out == {"U_FIN": "Finance", "U_ENG": "Engineering"}


def test_build_agenda_parses_dedupes_and_drops_malformed(monkeypatch):
    monkeypatch.setattr(agents, "Runner", _fake_runner(
        '{"decision":"Pick Q3 vendor","owner":"Ada","agenda":['
        '{"id":"budget","text":"Agree budget cap"},'
        '{"id":"budget","text":"dup id"},'        # duplicate id -> dropped
        '{"id":"","text":"empty id"},'            # empty id -> dropped
        '{"text":"no id key"},'                   # missing id -> dropped
        '{"id":"vendor","text":"Choose A vs B"}]}'))
    out = asyncio.run(t.build_agenda("setup"))
    assert out["decision"] == "Pick Q3 vendor" and out["owner"] == "Ada"
    assert [a["id"] for a in out["agenda"]] == ["budget", "vendor"]


def test_build_agenda_bad_json_is_empty(monkeypatch):
    monkeypatch.setattr(agents, "Runner", _fake_runner("not json"))
    assert asyncio.run(t.build_agenda("x")) == {"decision": "", "owner": "", "agenda": []}


def test_ground_reply_filters_to_agenda_ids_and_valid_positions(monkeypatch):
    agenda = [{"id": "budget", "text": "b"}, {"id": "vendor", "text": "v"}]
    monkeypatch.setattr(agents, "Runner", _fake_runner(
        '[{"item_id":"budget","position":"support","rationale":"r","key_assumptions":["a"]},'
        '{"item_id":"ghost","position":"block","rationale":"x","key_assumptions":[]},'   # bad id
        '{"item_id":"vendor","position":"wizard","rationale":"x","key_assumptions":[]}]'))  # bad pos
    out = asyncio.run(t.ground_reply("Finance", "reply", agenda))
    assert [g["item_id"] for g in out] == ["budget"]      # ghost id + wizard position dropped
    assert out[0]["position"] == "support" and out[0]["key_assumptions"] == ["a"]
