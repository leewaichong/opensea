"""Free-form DM entry point: the bot deduces intent and spins the flow up itself.

Demo path (no LLM): a parseable roster goes straight to one-shot fan-out; prep intent with no
roster opens a setup session; anything else falls through to the persistent-agent chat (which
is stubbed so the test makes no OpenAI call).
"""
import pmle.slack_app as s


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

    def say(*args, **kwargs):
        said.append(kwargs.get("text", args[0] if args else None))
    return say, said


def _dm(user, text):
    return {"channel_type": "im", "user": user, "text": text}


def _reset(monkeypatch):
    monkeypatch.delenv("PMLE_LIVE_AGENTS", raising=False)
    monkeypatch.setattr(s, "_PENDING_MEETINGS", {})
    monkeypatch.setattr(s, "_USER_TO_MEETING", {})
    monkeypatch.setattr(s, "_MANUAL_SESSIONS", {})


def test_freeform_with_roster_starts_multihuman_one_shot(monkeypatch):
    _reset(monkeypatch)
    client = FakeClient()
    say, _ = _say_collector()

    s.on_dm(_dm("U_OWNER",
                "let's prep the 11.11 mix — <@U_SHANG> commerce, <@U_JT> lead, me growth"),
            say, client)

    # No slash command, no setup turn — the opening message alone spun up the meeting.
    meeting = s._PENDING_MEETINGS["U_OWNER"]
    assert meeting.participants == {"U_SHANG": "Commerce", "U_JT": "Lead", "U_OWNER": "Growth"}
    assert {"dm_U_SHANG", "dm_U_JT"} <= {p["channel"] for p in client.posts}
    assert "U_OWNER" not in s._MANUAL_SESSIONS


def test_freeform_intent_without_roster_asks_for_setup(monkeypatch):
    _reset(monkeypatch)
    client = FakeClient()
    say, said = _say_collector()

    s.on_dm(_dm("U_OWNER", "can you help me prep a meeting?"), say, client)

    assert s._MANUAL_SESSIONS["U_OWNER"]["step"] == "setup"
    assert s._MANUAL_SESSIONS["U_OWNER"]["inputs"]["brief"] == "can you help me prep a meeting?"
    assert s._PENDING_MEETINGS == {}
    assert said and said[-1] == s.manual_flow.SETUP_PROMPT


def test_extract_roster_demo_uses_keyword(monkeypatch):
    monkeypatch.delenv("PMLE_LIVE_AGENTS", raising=False)
    text = "- <@U_SHANG> Commerce\n- <@U_JT> Lead\n- me Growth"
    assert s._extract_roster(text, "U_OWNER") == \
        s.meeting_mod.parse_participants(text, initiator="U_OWNER")


def test_extract_roster_live_infers_roles_via_llm(monkeypatch):
    monkeypatch.setenv("PMLE_LIVE_AGENTS", "1")

    async def fake_roster(text, targets):
        # NL with no literal role words — the LLM is what maps it.
        return {"U_WC": "Growth"}
    monkeypatch.setattr(s.triage, "llm_roster", fake_roster)

    out = s._extract_roster("<@U_WC> is driving our acquisition push", "U_OWNER")
    assert out == {"U_WC": "Growth"}


def test_extract_roster_live_no_mentions_skips_llm(monkeypatch):
    monkeypatch.setenv("PMLE_LIVE_AGENTS", "1")

    async def boom(text, targets):
        raise AssertionError("llm_roster must not be called when there are no @mentions")
    monkeypatch.setattr(s.triage, "llm_roster", boom)

    assert s._extract_roster("can you help me prep a meeting?", "U_OWNER") == {}


def test_nonmeeting_dm_falls_through_to_agent(monkeypatch):
    _reset(monkeypatch)

    class _FakeResult:
        final_output = "(noted)"

    class _FakeRunner:
        @staticmethod
        async def run(agent, text, session=None):
            return _FakeResult()

    # Stub the agent so no real OpenAI call happens on the fallback branch.
    monkeypatch.setattr(s, "build_participant", lambda person: (object(), object()))
    monkeypatch.setattr(s, "Runner", _FakeRunner)

    client = FakeClient()
    say, said = _say_collector()
    s.on_dm(_dm("U_X", "hey what's the weather today"), say, client)

    assert s._PENDING_MEETINGS == {} and s._MANUAL_SESSIONS == {}
    assert said[-1] == "(noted)"
