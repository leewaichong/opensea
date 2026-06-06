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

    async def fake_roster(text, targets, open_roles=False):
        # NL with no literal role words — the LLM is what maps it.
        return {"U_WC": "Growth"}
    monkeypatch.setattr(s.triage, "llm_roster", fake_roster)

    out = s._extract_roster("<@U_WC> is driving our acquisition push", "U_OWNER")
    assert out == {"U_WC": "Growth"}


def test_extract_roster_live_no_mentions_skips_llm(monkeypatch):
    monkeypatch.setenv("PMLE_LIVE_AGENTS", "1")

    async def boom(text, targets, open_roles=False):
        raise AssertionError("llm_roster must not be called when there are no @mentions")
    monkeypatch.setattr(s.triage, "llm_roster", boom)

    assert s._extract_roster("can you help me prep a meeting?", "U_OWNER") == {}


def test_tagged_but_unplaceable_asks_to_clarify_not_solo(monkeypatch):
    # A mention with no role keyword: demo parse can't place them. The bot must ASK, not fall
    # into the solo self-interview (which would spam the sender with every role prompt).
    _reset(monkeypatch)
    client = FakeClient()
    say, said = _say_collector()

    s.on_dm(_dm("U_OWNER", "<@U_SHANG> can you take a look at this?"), say, client)

    assert s._PENDING_MEETINGS == {}                      # no meeting started
    assert s._MANUAL_SESSIONS["U_OWNER"]["step"] == "setup"
    assert "couldn't tell what role" in said[-1]
    # Must NOT have sent a Growth/Commerce review prompt to the sender.
    assert not any("review" in (x or "").lower() for x in said)


def test_manual_setup_tagged_unplaceable_does_not_solo(monkeypatch):
    # Same guard inside the setup-session path: tagged-but-unplaceable stays in setup, no solo.
    _reset(monkeypatch)
    s._MANUAL_SESSIONS["U_OWNER"] = {"step": "setup", "inputs": {"brief": "prep a meeting"}}
    client = FakeClient()
    say, said = _say_collector()

    s._handle_manual_turn("U_OWNER", "<@U_SHANG> please review", say, client)

    assert s._PENDING_MEETINGS == {}
    assert s._MANUAL_SESSIONS["U_OWNER"]["step"] == "setup"   # didn't advance to growth
    assert "couldn't tell what role" in said[-1]


def test_clear_keyword_resets_and_escapes_state(monkeypatch):
    _reset(monkeypatch)
    s._MANUAL_SESSIONS["U_OWNER"] = {"step": "setup", "inputs": {}}
    calls = []
    # Stub the scenario reset (session-clear + reseed touch real DBs); test the routing.
    monkeypatch.setattr(s, "_reset_scenario", lambda: calls.append("scenario"))
    client = FakeClient()
    say, said = _say_collector()

    s.on_dm(_dm("U_OWNER", "  CLEAR  "), say, client)        # case/space-insensitive

    assert "U_OWNER" not in s._MANUAL_SESSIONS
    assert calls == ["scenario"]
    assert "beginning" in said[-1].lower()


def test_partial_placement_surfaces_unplaced_users(monkeypatch):
    # Live roster places only 1 of 2 tagged users. The meeting starts with the placed one, but
    # the un-placed teammate must be surfaced, not silently dropped. Pin hardcoded so the shared
    # _start_multihuman path doesn't call the real build_agenda.
    monkeypatch.setenv("PMLE_LIVE_AGENTS", "1")
    monkeypatch.setenv("PMLE_HARDCODED", "1")
    monkeypatch.setattr(s, "_PENDING_MEETINGS", {})
    monkeypatch.setattr(s, "_USER_TO_MEETING", {})
    monkeypatch.setattr(s, "_MANUAL_SESSIONS", {})

    async def fake_roster(text, targets, open_roles=False):
        return {"U_SHANG": "Commerce"}            # U_WC tagged but not placed
    monkeypatch.setattr(s.triage, "llm_roster", fake_roster)

    client = FakeClient()
    say, said = _say_collector()
    s.on_dm(_dm("U_OWNER", "<@U_SHANG> owns GMV and <@U_WC> helps out"), say, client)

    meeting = s._PENDING_MEETINGS["U_OWNER"]
    assert "U_SHANG" in meeting.participants
    assert "U_WC" not in meeting.participants
    assert any("U_WC" in (x or "") and "Couldn't include" in (x or "") for x in said)


def test_unreachable_participant_is_dropped_not_awaited(monkeypatch):
    from slack_sdk.errors import SlackApiError
    _reset(monkeypatch)

    class PickyClient(FakeClient):
        def conversations_open(self, users):
            if users == "U_GHOST":
                raise SlackApiError("nope", {"error": "user_not_found"})
            return super().conversations_open(users)

    client = PickyClient()
    say, said = _say_collector()
    s._start_multihuman("U_OWNER", {"inputs": {"brief": "b", "setup": "s"}},
                        {"U_SHANG": "Commerce", "U_GHOST": "Growth"}, say, client)

    meeting = s._PENDING_MEETINGS["U_OWNER"]
    assert "U_GHOST" not in meeting.participants     # not waited on -> can still auto-compile
    assert "U_SHANG" in meeting.participants
    assert any("U_GHOST" in (x or "") and "Couldn't include" in (x or "") for x in said)


def test_all_unreachable_aborts_without_stuck_meeting(monkeypatch):
    from slack_sdk.errors import SlackApiError
    _reset(monkeypatch)

    class DeadClient(FakeClient):
        def conversations_open(self, users):
            raise SlackApiError("nope", {"error": "user_not_found"})

    client = DeadClient()
    say, said = _say_collector()
    s._start_multihuman("U_OWNER", {"inputs": {}}, {"U_GHOST": "Growth"}, say, client)

    assert s._PENDING_MEETINGS == {}                 # no stuck meeting created
    assert any("couldn't message" in (x or "") for x in said)


def test_reset_flow_state_tears_down_owned_meeting(monkeypatch):
    _reset(monkeypatch)
    m = s.meeting_mod.Meeting(initiator="U_O", participants={"U_A": "Growth", "U_O": "Lead"})
    s._PENDING_MEETINGS["U_O"] = m
    s._USER_TO_MEETING.update({"U_O": "U_O", "U_A": "U_O"})

    cleared = s._reset_flow_state("U_O")

    assert s._PENDING_MEETINGS == {} and s._USER_TO_MEETING == {}
    assert "pending meeting" in cleared


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
