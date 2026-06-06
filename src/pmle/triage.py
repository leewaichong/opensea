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


_OPEN_ROSTER_AGENT = Agent(
    name="Roster Reader (open)",
    instructions=(
        "You read a meeting-setup message and assign each @mentioned teammate a SHORT role "
        "label (1-3 words) describing what they own in THIS meeting — e.g. 'Finance', "
        "'Engineering', 'Design', 'Growth', 'Legal' — inferred from how the message describes "
        "them, not from a fixed list.\n"
        "You are given the message and the EXACT Slack user IDs that were mentioned. Return "
        "STRICT JSON mapping user ID -> short role label, using ONLY those IDs. Omit anyone "
        'whose role you genuinely cannot tell. Example: {"U_AB": "Finance"}.'
    ),
)


async def llm_roster(text: str, target_ids: list[str], open_roles: bool = False) -> dict[str, str]:
    """Live-mode role assignment: infer each mentioned user's role from the natural language.

    IDs come in pre-extracted (exact); this only decides the role. Anything the model returns
    outside the given IDs is dropped, so a hallucinated id can't leak in. With open_roles the
    label is free text (dynamic mode); otherwise it's filtered to the three fixed roles."""
    from agents import Runner

    agent = _OPEN_ROSTER_AGENT if open_roles else _ROSTER_AGENT
    prompt = (f"Setup message:\n{text}\n\n"
              f"Mentioned Slack user IDs: {target_ids}\n"
              "Assign each of those IDs a role from the message.")
    result = await Runner.run(agent, prompt)
    raw = result.final_output.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    try:
        data = json.loads(raw)
    except ValueError:
        return {}
    allowed = set(target_ids)
    if open_roles:
        return {k: str(v).strip() for k, v in data.items()
                if k in allowed and isinstance(v, str) and v.strip()}
    return {k: v for k, v in data.items() if k in allowed and v in _VALID_ROLES}


# --- Dynamic live flow: generate the agenda from the setup, ground real replies onto it ---

_AGENDA_BUILDER = Agent(
    name="Agenda Builder",
    instructions=(
        "You read a meeting-setup message and extract the structure needed to prepare it.\n"
        'Return STRICT JSON: {"decision": str, "owner": str, '
        '"agenda": [{"id": str, "text": str}, ...]}.\n'
        "- decision: one sentence naming the decision/outcome the meeting must reach.\n"
        "- owner: who owns the decision (a name or role from the message), or \"\" if unclear.\n"
        "- agenda: 3-9 concrete discussion items implied by the setup. id = short kebab-case "
        "slug (e.g. \"budget-split\"); text = the agenda line. Use the user's listed agenda if "
        "they gave one; otherwise infer items from the decision and context.\n"
        "Output ONLY the JSON."
    ),
)


async def build_agenda(setup_text: str) -> dict:
    """Generate {decision, owner, agenda:[{id,text}]} from the initiator's free-form setup."""
    from agents import Runner

    result = await Runner.run(_AGENDA_BUILDER, setup_text)
    raw = result.final_output.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    try:
        data = json.loads(raw)
    except ValueError:
        return {"decision": "", "owner": "", "agenda": []}
    agenda, seen = [], set()
    for it in data.get("agenda", []) if isinstance(data, dict) else []:
        if isinstance(it, dict) and it.get("id") and it.get("text"):
            iid = str(it["id"]).strip()
            if iid and iid not in seen:
                seen.add(iid)
                agenda.append({"id": iid, "text": str(it["text"]).strip()})
    return {"decision": str(data.get("decision", "")).strip(),
            "owner": str(data.get("owner", "")).strip(),
            "agenda": agenda}


_POSITIONS = ("support", "agree_with_condition", "neutral", "block")

_GROUNDER = Agent(
    name="Stance Grounder",
    instructions=(
        "You convert one person's free-form meeting input into structured stances on specific "
        "agenda items. You are given their role, their message, and the agenda (ids + text).\n"
        "For each agenda item their message actually speaks to, output a stance. Do NOT invent "
        "stances for items they didn't address.\n"
        'Return STRICT JSON array: [{"item_id": str, "position": one of '
        '["support","agree_with_condition","neutral","block"], "rationale": str, '
        '"key_assumptions": [str, ...]}].\n'
        "Use ONLY item_ids from the given agenda. Output ONLY the JSON array."
    ),
)


async def ground_reply(role: str, reply: str, agenda: list[dict]) -> list[dict]:
    """Map a real person's reply onto stances over the meeting's actual agenda. Stances are
    filtered to the exact agenda ids and valid positions, so a hallucinated item_id can't
    scatter input under a phantom topic (which would make Mochi silently see nothing)."""
    from agents import Runner

    valid = {a["id"] for a in agenda}
    agenda_txt = "\n".join(f"- {a['id']}: {a['text']}" for a in agenda)
    prompt = (f"Role: {role}\n\nTheir message:\n{reply}\n\nAgenda items:\n{agenda_txt}\n\n"
              "Produce their stances as JSON.")
    result = await Runner.run(_GROUNDER, prompt)
    raw = result.final_output.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    try:
        data = json.loads(raw)
    except ValueError:
        return []
    out = []
    for s in data if isinstance(data, list) else []:
        if isinstance(s, dict) and s.get("item_id") in valid and s.get("position") in _POSITIONS:
            out.append({"item_id": s["item_id"], "position": s["position"],
                        "rationale": str(s.get("rationale", "")),
                        "key_assumptions": [str(x) for x in (s.get("key_assumptions") or [])]})
    return out
