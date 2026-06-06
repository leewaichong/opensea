"""Intent triage for the free-form DM entry point.

There is no slash command to start a pre-meeting anymore: the user just talks to the bot
in a DM and the bot deduces whether they're asking to prepare/align a meeting. This module
holds the Slack-free intent check. Two modes, mirroring the rest of the app's gate:

  demo (PMLE_LIVE_AGENTS unset/0): a deterministic keyword heuristic — offline, no API key,
      anchored on prep intent so ordinary DMs don't spuriously spin up a meeting.
  live (PMLE_LIVE_AGENTS=1): a small router agent that classifies the message.

Roster extraction stays in `meeting.parse_participants`; the Slack layer treats a parseable
roster as intent on its own (an "@mention + role" message is self-evidently a meeting setup),
so this heuristic only has to catch the no-roster "help me prep a meeting" phrasing.
"""
import json
import re

from agents import Agent

from pmle.meeting import ROLE_TO_PERSONA

_VALID_ROLES = tuple(ROLE_TO_PERSONA)  # ("Growth", "Commerce", "Lead")

# Anchored on prep intent. `prep` (substring) covers prepare/preparing/prepped; `pre-meeting`
# tolerates a hyphen/space; `agenda` is unambiguous enough. Deliberately NOT firing on bare
# ambient words (sync/meeting/align/decide) which show up in ordinary chat.
_PREP_RE = re.compile(r"prep|pre[-\s]?meeting|agenda", re.IGNORECASE)


def heuristic_intent(text: str) -> bool:
    """Deterministic demo-mode intent check."""
    return bool(_PREP_RE.search(text or ""))


_ROUTER = Agent(
    name="Intake Router",
    instructions=(
        "You triage a single Slack DM sent to a meeting-prep assistant. Decide whether the "
        "message is a request to PREPARE or align a meeting: prep a pre-meeting, gather "
        "stakeholder input, compress an agenda, or align a group on a decision/option.\n"
        "Casual chat, status questions, file requests, or anything not about organizing a "
        "meeting -> false.\n"
        'Reply with STRICT JSON, nothing else: {"is_premeeting": true} or {"is_premeeting": false}.'
    ),
)


async def llm_intent(text: str) -> bool:
    """Live-mode intent check via the router agent."""
    from agents import Runner

    result = await Runner.run(_ROUTER, text)
    raw = result.final_output.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    try:
        return bool(json.loads(raw).get("is_premeeting"))
    except (ValueError, AttributeError):
        return "true" in raw.lower()


_ROSTER_AGENT = Agent(
    name="Roster Reader",
    instructions=(
        "You read a meeting-setup message and assign each @mentioned teammate a role, "
        "INFERRING it from how the message describes what they own — not from literal "
        "keywords. e.g. 'driving our acquisition push' -> Growth; 'owns the sale-window "
        "numbers' -> Commerce; 'running this call' -> Lead.\n"
        "Roles (choose exactly one per person):\n"
        "- Growth:   owns new-user acquisition / growth / installs.\n"
        "- Commerce: owns GMV / conversion / sales / the sale window.\n"
        "- Lead:     the campaign lead / decision owner / person running the meeting.\n"
        "You are given the message and the EXACT Slack user IDs that were mentioned. Return "
        "STRICT JSON mapping user ID -> role, using ONLY those IDs and ONLY the three roles "
        'above. Omit anyone whose role you genuinely cannot tell. Example: {"U_WC": "Growth"}.'
    ),
)


async def llm_roster(text: str, target_ids: list[str]) -> dict[str, str]:
    """Live-mode role assignment: infer each mentioned user's role from the natural language.

    IDs come in pre-extracted (exact); this only decides the role. Anything the model returns
    outside the given IDs or the three valid roles is dropped, so a hallucinated id/role can't
    leak into the meeting."""
    from agents import Runner

    prompt = (f"Setup message:\n{text}\n\n"
              f"Mentioned Slack user IDs: {target_ids}\n"
              "Assign each of those IDs a role from the message.")
    result = await Runner.run(_ROSTER_AGENT, prompt)
    raw = result.final_output.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    try:
        data = json.loads(raw)
    except ValueError:
        return {}
    allowed = set(target_ids)
    return {k: v for k, v in data.items() if k in allowed and v in _VALID_ROLES}
