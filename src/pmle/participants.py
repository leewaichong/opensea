from agents import Agent, Runner, SQLiteSession, function_tool
from pmle.schemas import Stance
from pmle.stance_store import StanceStore
from pmle.data.personas import PERSONAS

_STORE = StanceStore()


def _make_tools(person: str):
    @function_tool
    def get_stance(item_id: str) -> str:
        """Return the person's current stance JSON for an agenda item, or 'none'."""
        s = _STORE.get(person, item_id)
        return s.model_dump_json() if s else "none"

    @function_tool
    def set_stance(item_id: str, position: str, rationale: str,
                   key_assumptions: list[str], confidence: float = 0.7) -> str:
        """Create/replace the person's stance on an item from explicit fields."""
        s = Stance(stakeholder=person, item_id=item_id, position=position,
                   rationale=rationale, key_assumptions=key_assumptions, confidence=confidence)
        _STORE.set(person, s)
        return s.model_dump_json()

    @function_tool
    def update_stance(item_id: str, position: str = "", rationale: str = "",
                      key_assumptions: list[str] | None = None) -> str:
        """Patch only the provided fields of the person's existing stance."""
        partial = {k: v for k, v in
                   {"position": position, "rationale": rationale,
                    "key_assumptions": key_assumptions}.items() if v}
        return _STORE.update(person, item_id, partial).model_dump_json()

    return [get_stance, set_stance, update_stance]


def build_participant(person: str) -> tuple[Agent, SQLiteSession]:
    persona = PERSONAS[person]
    agent = Agent(
        name=f"{person} Agent",
        instructions=(
            f"You are {person}'s personal work agent. Private context:\n{persona['private']}\n\n"
            "When your human messages you, map what they say onto their stance using the "
            "set_stance/update_stance tools. When the orchestrator asks for your stance on an "
            "item, call get_stance; if empty, answer from your private context and persist it "
            "with set_stance. Be concise. Output the stance as JSON when asked by the orchestrator."
        ),
        tools=_make_tools(person),
    )
    # Persistent session — survives across meetings (enterprise standing agent).
    session = SQLiteSession(f"participant::{person}", "pmle_sessions.db")
    return agent, session


async def ask_stance(person: str, item_id: str, item_text: str) -> Stance:
    """Used by the orchestrator (via as_tool wrapper) to get a participant's current stance."""
    agent, session = build_participant(person)
    existing = _STORE.get(person, item_id)
    if existing:
        return existing
    prompt = (f"Agenda item '{item_id}': {item_text}. Provide your stance and persist it "
              f"with set_stance. Then output the stance JSON.")
    await Runner.run(agent, prompt, session=session)
    return _STORE.get(person, item_id) or Stance(
        stakeholder=person, item_id=item_id, position="neutral",
        rationale="No stance available.", key_assumptions=[])
