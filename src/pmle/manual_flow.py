"""Pure session state machine for the hosted /premeeting flow.

No Slack, no LLM, no I/O — just the conversation state transitions so the flow is
unit-testable. `slack_app` layers the side effects (grounding stakeholder input into
the stance store, generating the brief) on top of the structured signals returned here.
"""

# Ordered steps. The conversation walks brief -> setup -> growth -> commerce ->
# owner_gap -> confirm_growth -> confirm_commerce -> complete.
FIRST_PROMPT = (
    "What meeting do you want to prepare?\n\n"
    "Tell me the decision you need the meeting to resolve, who should be involved, "
    "and what kind of agenda compression you want. A rough paragraph is enough."
)

SETUP_PROMPT = (
    "Got it. I can host that pre-meeting.\n\n"
    "Send me the setup so I can collect the right stakeholder input:\n"
    "- meeting title\n"
    "- decision owner\n"
    "- participants and roles\n"
    "- known candidates/options\n"
    "- initial agenda\n"
    "- constraints or context"
)

GROWTH_PROMPT = (
    "Thanks — I have the setup. I'll collect stakeholder views before compressing the agenda.\n\n"
    "*Growth review*\n"
    "What's the growth/acquisition take?\n"
    "1. Which option best supports new-user growth?\n"
    "2. Which agenda item must stay in the live meeting?\n"
    "3. Which items are already safe to treat as agreed?\n"
    "4. What assumption should I preserve in the brief?"
)

COMMERCE_PROMPT = (
    "*Commerce review*\n"
    "What's the commerce/conversion take?\n"
    "1. Which option best supports sale-window GMV?\n"
    "2. Which agenda item must stay in the live meeting?\n"
    "3. Which items are already safe to treat as agreed?\n"
    "4. What assumption should I preserve in the brief?"
)

OWNER_GAP_PROMPT = (
    "I'm seeing a likely alignment gap: the stakeholders may share the same audience label "
    "but optimize different outcomes — acquisition, GMV/conversion, or mainstream brand reach.\n\n"
    "From the decision-owner side, what should the plan optimize for? Or should the live agenda "
    "explicitly decide the split between those objectives?"
)

CONFIRM_GROWTH_PROMPT = (
    "Owner perspective captured. I'm moving resolved items into the pre-read.\n\n"
    "*Growth check:* comfortable moving deliverables, tracking, hero categories, and backup "
    "options into consensus? Any caveat I should preserve?"
)

CONFIRM_COMMERCE_PROMPT = (
    "*Commerce check:* comfortable moving deliverables, hero categories, and backup options "
    "into consensus? Any caveat I should preserve?"
)

GENERATING_PROMPT = (
    "Inputs captured. Generating your compressed pre-meeting brief from what you gave me…"
)

# Which participant each step's free-form reply should be grounded into.
_GROUND_BY_STEP = {
    "growth": "Wai Chong",
    "commerce": "Shang",
    "owner_gap": "John Taylor",
}

# Light heuristics: which setup fields look present in the user's setup message.
_SETUP_FIELDS = {
    "meeting title": ("title",),
    "participants": ("participant", "role"),
    "agenda": ("agenda",),
}


def new_session() -> dict:
    """Fresh manual-flow session state."""
    return {"step": "brief", "inputs": {}}


def missing_setup_fields(text: str) -> list[str]:
    """Return the setup fields whose signal keywords are absent from `text`."""
    low = text.lower()
    return [label for label, keys in _SETUP_FIELDS.items()
            if not any(k in low for k in keys)]


def _missing_setup_prompt(missing: list[str]) -> str:
    return ("I still need a bit more setup before I can collect stakeholder input. "
            "Please add: " + ", ".join(missing) + ".")


def advance_manual_flow(session: dict, text: str) -> dict:
    """Record `text` for the current step, advance the state machine, and return the
    signals the Slack layer needs.

    Returns a dict with:
      - reply (str): the next bot prompt to send.
      - ground (tuple[str, str] | None): (participant, text) to ground into the stance
        store, or None when this step carries no stakeholder stance.
      - complete (bool): True when all inputs are collected and the brief should be built.
    """
    step = session.get("step", "brief")
    session.setdefault("inputs", {})[step] = text
    ground = None
    complete = False

    if step == "brief":
        session["step"] = "setup"
        reply = SETUP_PROMPT
    elif step == "setup":
        missing = missing_setup_fields(text)
        if missing:
            # Stay on setup and ask only for what's missing — dynamic, not lockstep.
            reply = _missing_setup_prompt(missing)
        else:
            session["step"] = "growth"
            reply = GROWTH_PROMPT
    elif step == "growth":
        ground = (_GROUND_BY_STEP["growth"], text)
        session["step"] = "commerce"
        reply = COMMERCE_PROMPT
    elif step == "commerce":
        ground = (_GROUND_BY_STEP["commerce"], text)
        session["step"] = "owner_gap"
        reply = OWNER_GAP_PROMPT
    elif step == "owner_gap":
        ground = (_GROUND_BY_STEP["owner_gap"], text)
        session["step"] = "confirm_growth"
        reply = CONFIRM_GROWTH_PROMPT
    elif step == "confirm_growth":
        session["step"] = "confirm_commerce"
        reply = CONFIRM_COMMERCE_PROMPT
    else:  # confirm_commerce (or any trailing input) -> generate the brief
        session["step"] = "complete"
        complete = True
        reply = GENERATING_PROMPT

    return {"reply": reply, "ground": ground, "complete": complete}
