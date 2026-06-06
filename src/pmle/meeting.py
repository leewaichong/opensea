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
_ROLE_RE = re.compile(r"\b(growth|commerce|lead)\b", re.IGNORECASE)
# Slack mention: <@U123> or <@U123|name>  (underscores tolerated for robustness)
_MENTION = re.compile(r"<@([A-Z0-9_]+)(?:\|[^>]+)?>")
_ME = re.compile(r"\b(?:me|myself)\b", re.IGNORECASE)


def parse_participants(text: str, initiator: str | None = None) -> dict[str, str]:
    """Parse participant lines into {slack_user_id: role}.

    Works per line, pairing each target (an @mention, or 'me'/'myself' -> `initiator`) with
    the nearest role word (growth/commerce/lead) — preferring one that *follows* the target,
    since people write "<@U1> Commerce" and "me, Growth Lead". This handles both the bulleted
    multi-line setup AND a one-line "<@U1> commerce, <@U2> lead, me growth", and tolerates a
    comma between the mention and its role ("<@U1> , Growth Lead"). A line with no role word,
    or a target with no role on its line, yields nothing — and a setup with no @mentions/me
    returns {}, the signal to stay in the solo flow."""
    roster: dict[str, str] = {}
    for line in text.splitlines():
        roles = [(m.start(), _ROLE_WORDS[m.group(1).lower()]) for m in _ROLE_RE.finditer(line)]
        if not roles:
            continue
        targets = [(m.start(), m.group(1)) for m in _MENTION.finditer(line)]
        if initiator:
            targets += [(m.start(), initiator) for m in _ME.finditer(line)]
        for pos, uid in targets:
            following = [r for r in roles if r[0] >= pos]
            nearest = min(following or roles, key=lambda r: abs(r[0] - pos))
            roster[uid] = nearest[1]
    return roster


def extract_targets(text: str, initiator: str | None = None) -> list[str]:
    """Deterministically pull the Slack user IDs to assign roles to: every @mention, plus the
    initiator when they refer to themselves ('me'/'myself') *alongside* mentions. IDs must be
    exact, so this stays regex-based; the live path then asks an LLM to infer each one's role
    from the free-form text. A lone 'me' with no @mentions returns [] — nobody to coordinate."""
    ids: list[str] = []
    for m in _MENTION.finditer(text):
        if m.group(1) not in ids:
            ids.append(m.group(1))
    if initiator and ids and initiator not in ids and _ME.search(text):
        ids.append(initiator)
    return ids


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
