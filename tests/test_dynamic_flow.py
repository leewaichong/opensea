"""Full dynamic live flow (PMLE_HARDCODED unset): the agenda, roles, and stances come from the
real setup + real replies — no Shopee, no fixed personas. The LLM functions are mocked so the
wiring is exercised without any OpenAI call.
"""
import pmle.slack_app as s
from pmle.schemas import ClassificationResult


class FakeClient:
    def __init__(self):
        self.posts = []

    def conversations_open(self, users):
        return {"channel": {"id": f"dm_{users}"}}

    def chat_postMessage(self, channel, text=None, blocks=None):
        self.posts.append({"channel": channel, "text": text, "blocks": blocks})
        return {"ok": True}


def _say_collector():
    said = []

    def say(*a, **k):
        said.append(k.get("text", a[0] if a else None))
    return say, said


def _dm(user, text):
    return {"channel_type": "im", "user": user, "text": text}


def _setup_dynamic(monkeypatch):
    monkeypatch.setenv("PMLE_LIVE_AGENTS", "1")
    monkeypatch.delenv("PMLE_HARDCODED", raising=False)        # -> dynamic
    monkeypatch.setattr(s, "_PENDING_MEETINGS", {})
    monkeypatch.setattr(s, "_USER_TO_MEETING", {})
    monkeypatch.setattr(s, "_MANUAL_SESSIONS", {})

    async def fake_roster(text, targets, open_roles=False):
        assert open_roles is True                              # dynamic uses free-text roles
        return {"U_FIN": "Finance", "U_ENG": "Engineering"}

    async def fake_agenda(setup):
        return {"decision": "Pick the Q3 infra vendor", "owner": "Ada",
                "agenda": [{"id": "budget", "text": "Agree the budget cap"},
                           {"id": "vendor", "text": "Choose vendor A vs vendor B"}]}

    async def fake_ground(role, reply, agenda):
        # Both speak to 'vendor' (so it's contested); nobody touches 'budget'.
        return [{"item_id": "vendor",
                 "position": "support" if role == "Finance" else "block",
                 "rationale": f"{role} view", "key_assumptions": [f"{role} assumption"]}]

    async def fake_classify(stances):
        item = stances[0].item_id
        return ClassificationResult(
            item_id=item, status="crux" if len(stances) > 1 else "agreed",
            summary=f"{item} summary", cited_stances=[st.stakeholder for st in stances])

    monkeypatch.setattr(s.triage, "llm_roster", fake_roster)
    monkeypatch.setattr(s.triage, "build_agenda", fake_agenda)
    monkeypatch.setattr(s.triage, "ground_reply", fake_ground)
    monkeypatch.setattr(s, "classify_item", fake_classify)


def test_dynamic_flow_real_agenda_grounding_and_brief(monkeypatch):
    _setup_dynamic(monkeypatch)
    client = FakeClient()
    say, said = _say_collector()

    s.on_dm(_dm("U_OWNER",
                "help me prep: pick the Q3 infra vendor. <@U_FIN> finance, <@U_ENG> eng"),
            say, client)

    meeting = s._PENDING_MEETINGS["U_OWNER"]
    # Agenda + decision came from the setup, not the fixed Shopee scenario.
    assert meeting.decision == "Pick the Q3 infra vendor"
    assert [a["id"] for a in meeting.agenda] == ["budget", "vendor"]
    assert meeting.participants == {"U_FIN": "Finance", "U_ENG": "Engineering"}
    # Review prompts reference the REAL agenda; nothing Shopee leaks in.
    fanout = str(client.posts) + str(said)
    assert "Choose vendor A vs vendor B" in fanout
    assert "Shopee" not in fanout

    # Replies grounded onto the real agenda, keyed by slack id, stance labelled by role.
    s._handle_meeting_dm("U_FIN", "budget cap fine, vendor A", say, client)
    s._handle_meeting_dm("U_ENG", "vendor B is the only viable one", say, client)
    assert "vendor" in meeting.stances["U_FIN"]
    assert meeting.stances["U_FIN"]["vendor"].stakeholder == "Finance"

    # Auto-compiled once both replied; the brief is about the real decision.
    assert meeting.phase == "done"
    briefs = [p for p in client.posts if p.get("blocks")]
    assert briefs, "a Block Kit brief was posted"
    blob = str(briefs)
    assert "Pick the Q3 infra vendor" in blob
    # 'vendor' was contested (crux -> needs the meeting); 'budget' had no input -> flagged,
    # NOT folded into consensus.
    assert "Needs the live meeting" in blob
    assert "No input yet" in blob and "Agree the budget cap" in blob
    assert "Shopee" not in blob


def test_same_role_participants_do_not_clobber(monkeypatch):
    # Two people both inferred as 'Engineering' must each keep their own stance (keyed by id).
    _setup_dynamic(monkeypatch)

    async def fake_roster(text, targets, open_roles=False):
        return {"U_E1": "Engineering", "U_E2": "Engineering"}
    monkeypatch.setattr(s.triage, "llm_roster", fake_roster)

    client = FakeClient()
    say, _ = _say_collector()
    s.on_dm(_dm("U_OWNER", "prep the vendor pick. <@U_E1> eng, <@U_E2> eng"), say, client)
    meeting = s._PENDING_MEETINGS["U_OWNER"]

    s._handle_meeting_dm("U_E1", "vendor A", say, client)
    s._handle_meeting_dm("U_E2", "vendor B", say, client)

    assert set(meeting.stances) == {"U_E1", "U_E2"}        # both retained, no clobber
    assert meeting.stances["U_E1"]["vendor"].rationale == "Engineering view"
