"""Pure helpers for the multi-participant /premeeting flow.

The orchestrator reaches out to the *real* people in a meeting: the initiator @mentions
each participant with a role in the setup message, the bot DMs each of them, and grounds
their reply into that role's persona Stance. This module is the Slack-free, LLM-free core:
parse the participant roster, map roles to personas, and track who has responded.
"""
import re
from dataclasses import dataclass, field

# Real Slack users are mapped to the existing seeded personas by role, so the orchestrator,
# agenda, and stance store stay unchanged.
ROLE_TO_PERSONA = {"Growth": "Wai Chong", "Commerce": "Shang", "Lead": "John Taylor"}

_ROLE_WORDS = {"growth": "Growth", "commerce": "Commerce", "lead": "Lead"}
# Slack mention: <@U123> or <@U123|name>  (underscores tolerated for robustness)
_MENTION = re.compile(r"<@([A-Z0-9_]+)(?:\|[^>]+)?>")
_ME = re.compile(r"\b(me|myself)\b", re.IGNORECASE)


def parse_participants(text: str, initiator: str | None = None) -> dict[str, str]:
    """Parse '<@U123> Commerce' / 'me -> Growth' lines into {slack_user_id: role}.

    A line counts only if it has BOTH a recognized role word (growth/commerce/lead) and a
    target (an @mention, or 'me'/'myself' which resolves to `initiator`). Plain-name setups
    with no @mentions return {} — that's the signal to stay in the solo flow."""
    roster: dict[str, str] = {}
    for line in text.splitlines():
        low = line.lower()
        role = next((r for w, r in _ROLE_WORDS.items() if w in low), None)
        if not role:
            continue
        m = _MENTION.search(line)
        if m:
            roster[m.group(1)] = role
        elif initiator and _ME.search(line):
            roster[initiator] = role
    return roster


@dataclass
class Meeting:
    """In-flight multi-participant meeting state (one active meeting per initiator)."""
    initiator: str
    brief: str = ""
    setup: str = ""
    participants: dict[str, str] = field(default_factory=dict)  # slack_user_id -> role
    responses: dict[str, str] = field(default_factory=dict)     # slack_user_id -> reply text
    phase: str = "collecting"                                    # collecting | done

    def pending(self) -> list[str]:
        return [u for u in self.participants if u not in self.responses]

    def all_responded(self) -> bool:
        return bool(self.participants) and not self.pending()
