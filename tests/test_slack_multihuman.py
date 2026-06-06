"""Offline end-to-end test of the multi-participant /premeeting coordination.

Uses a fake Slack client + say (no Slack) and the deterministic demo brief path (no LLM),
so it exercises roster parsing -> fan-out DMs -> reply routing -> auto-compile without any
external dependency. CHANNEL is forced to None so the brief posts to the owner DM via the
fake client (never a real API call).
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


def test_multihuman_fanout_collect_and_compile(monkeypatch):
    monkeypatch.delenv("PMLE_LIVE_AGENTS", raising=False)      # demo path, no LLM
    monkeypatch.setattr(s, "CHANNEL", None)                    # brief -> owner DM, no real API
    monkeypatch.setattr(s, "_PENDING_MEETINGS", {})
    monkeypatch.setattr(s, "_USER_TO_MEETING", {})
    monkeypatch.setattr(s, "_MANUAL_SESSIONS",
                        {"U_OWNER": {"step": "setup", "inputs": {"brief": "prep the 11.11 meeting"}}})

    client = FakeClient()
    say, said = _say_collector()

    setup = ("Title: Shopee 11.11 Creator Mix\nParticipants:\n"
             "- <@U_SHANG> Commerce\n- <@U_JT> Lead\n- me Growth\nAgenda: align, role mix, ...")
    s._handle_manual_turn("U_OWNER", setup, say, client)

    # Roster parsed; initiator + 2 teammates routable; intake session cleared.
    meeting = s._PENDING_MEETINGS["U_OWNER"]
    assert meeting.participants == {"U_SHANG": "Commerce", "U_JT": "Lead", "U_OWNER": "Growth"}
    assert set(s._USER_TO_MEETING) == {"U_OWNER", "U_SHANG", "U_JT"}
    assert "U_OWNER" not in s._MANUAL_SESSIONS
    # The two non-initiator participants got DMed their review prompt.
    assert {"dm_U_SHANG", "dm_U_JT"} <= {p["channel"] for p in client.posts}

    # Replies trickle in; brief should NOT compile until all three are in.
    s._handle_meeting_dm("U_SHANG", "GMV focus, Jayden for Shopee Live.", say, client)
    assert not meeting.all_responded()
    s._handle_meeting_dm("U_JT", "Mainstream-safe youth reach.", say, client)
    assert meeting.pending() == ["U_OWNER"]
    assert meeting.phase == "collecting"

    # Final reply (initiator is also the Growth participant) triggers auto-compile.
    s._handle_meeting_dm("U_OWNER", "Acquisition, Mika as hero.", say, client)
    assert meeting.phase == "done"
    # A Block Kit brief was posted, and meeting state is cleaned up.
    assert any(p.get("blocks") for p in client.posts)
    assert s._PENDING_MEETINGS == {} and s._USER_TO_MEETING == {}


def test_owner_can_force_compile_early(monkeypatch):
    monkeypatch.delenv("PMLE_LIVE_AGENTS", raising=False)
    monkeypatch.setattr(s, "CHANNEL", None)
    monkeypatch.setattr(s, "_PENDING_MEETINGS", {})
    monkeypatch.setattr(s, "_USER_TO_MEETING", {})
    monkeypatch.setattr(s, "_MANUAL_SESSIONS",
                        {"U_OWNER": {"step": "setup", "inputs": {"brief": "b"}}})

    client = FakeClient()
    say, _ = _say_collector()
    s._handle_manual_turn("U_OWNER",
                          "Participants:\n- <@U_SHANG> Commerce\n- <@U_JT> Lead", say, client)
    meeting = s._PENDING_MEETINGS["U_OWNER"]
    assert not meeting.all_responded()

    # Owner force-compiles before anyone replied.
    s._handle_meeting_dm("U_OWNER", "compile", say, client)
    assert meeting.phase == "done"
    assert any(p.get("blocks") for p in client.posts)
