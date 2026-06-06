from pmle.meeting import Meeting, ROLE_TO_PERSONA, parse_participants, extract_targets

_SETUP = """Meeting title: Shopee SG 11.11 Creator Mix Planning
Decision owner: me, John Taylor
Participants:
- <@U_SHANG> Commerce
- <@U_JT|jaytee> Lead
- me Growth
Initial agenda: align objective, decide role mix, ..."""


def test_parse_participants_mentions_and_me():
    roster = parse_participants(_SETUP, initiator="U_OWNER")
    assert roster == {"U_SHANG": "Commerce", "U_JT": "Lead", "U_OWNER": "Growth"}


def test_parse_participants_handles_pipe_mention():
    # <@U_JT|jaytee> must resolve to the bare id U_JT.
    assert parse_participants("- <@U_JT|jaytee> Lead") == {"U_JT": "Lead"}


def test_parse_comma_between_mention_and_role():
    # Real format from a live test: a comma sits between the mention and the role title,
    # and the role is written as "<role> Lead" (e.g. "Growth Lead"). Must still parse.
    setup = ("Decision owner: me, John Taylor, 11.11 Campaign Lead.\n"
             "Participants:\n"
             "<@U_WC> , Growth Lead\n"
             "<@U_SH> , Commerce Lead\n"
             "myself, Campaign Lead")
    roster = parse_participants(setup, initiator="U_JT")
    assert roster == {"U_WC": "Growth", "U_SH": "Commerce", "U_JT": "Lead"}


def test_parse_single_line_multi_participant():
    # One-line free-form entry must split into three participants by position, no commas needed.
    text = "prep the 11.11 mix — <@U_SHANG> commerce, <@U_JT> lead, me growth"
    assert parse_participants(text, initiator="U_OWNER") == {
        "U_SHANG": "Commerce", "U_JT": "Lead", "U_OWNER": "Growth"}


def test_plain_names_without_mentions_stay_solo():
    # No <@...> and no initiator -> {}, so /premeeting stays in the solo flow.
    text = "Participants:\n- Wai Chong, Growth Lead\n- Shang, Commerce Lead"
    assert parse_participants(text) == {}


def test_me_needs_a_role_word_on_the_line():
    # 'Decision owner: me, John Taylor' has no role word -> not treated as a participant.
    assert parse_participants("Decision owner: me, John Taylor", initiator="U_OWNER") == {}


def test_extract_targets_mentions_and_me():
    # Live path: pull exact IDs (mentions + 'myself' alongside them). Roles come from the LLM,
    # so this is purely about *which* IDs, not their roles.
    text = "Participants:\n<@U_WC> drives acquisition\n<@U_SH> owns GMV\nmyself running the call"
    assert extract_targets(text, initiator="U_JT") == ["U_WC", "U_SH", "U_JT"]


def test_extract_targets_ignores_lone_me():
    # 'me' with no @mentions -> nobody to coordinate -> [], so live mode skips the LLM call.
    assert extract_targets("help me prep a meeting", initiator="U_JT") == []


def test_role_persona_mapping():
    assert ROLE_TO_PERSONA == {"Growth": "Wai Chong", "Commerce": "Shang", "Lead": "John Taylor"}


def test_meeting_response_tracking():
    m = Meeting(initiator="U_OWNER",
                participants={"U_SHANG": "Commerce", "U_JT": "Lead"})
    assert not m.all_responded()
    assert set(m.pending()) == {"U_SHANG", "U_JT"}

    m.responses["U_SHANG"] = "GMV focus, Jayden for Shopee Live."
    assert m.pending() == ["U_JT"]
    assert not m.all_responded()

    m.responses["U_JT"] = "Mainstream-safe youth reach."
    assert m.all_responded()


def test_empty_meeting_not_complete():
    assert Meeting(initiator="U_OWNER").all_responded() is False
