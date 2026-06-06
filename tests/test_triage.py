"""Demo-mode intent heuristic: fires on prep language, ignores ordinary chat."""
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
