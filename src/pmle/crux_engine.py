import json
from agents import Agent, Runner
from pmle.schemas import Stance, ClassificationResult

_CLASSIFIER = Agent(
    name="Crux Judge",
    instructions=(
        "You compare stakeholder stances on ONE agenda item. Use BOTH position AND "
        "key_assumptions. Classify as one of: agreed, crux, fake_agreement, "
        "needs_clarification.\n"
        "- agreed: positions align AND assumptions align.\n"
        "- crux: positions diverge in a way that affects the go/no-go.\n"
        "- fake_agreement: surface positions align but key_assumptions conflict.\n"
        "- needs_clarification: evidence/assumptions too thin to judge; do not guess.\n"
        "Return STRICT JSON with keys: status, summary, divergence, cited_stances, follow_up."
    ),
)


def naive_baseline(stances: list[Stance]) -> ClassificationResult:
    """Position-only classifier. Deliberately ignores assumptions so it MISSES fake agreement."""
    item_id = stances[0].item_id if stances else "unknown"
    positions = {s.position for s in stances}
    if "block" in positions:
        status = "crux"
    else:
        status = "agreed"
    return ClassificationResult(
        item_id=item_id, status=status,
        summary=f"Baseline (positions only): {sorted(positions)}",
        cited_stances=[s.stakeholder for s in stances],
    )


async def _llm_classify(prompt: str) -> dict:
    result = await Runner.run(_CLASSIFIER, prompt)
    text = result.final_output.strip()
    if text.startswith("```"):
        text = text.split("```")[1].lstrip("json").strip()
    return json.loads(text)


def _normalize_cited_stances(value, stances: list[Stance]) -> list[str]:
    if not value:
        return [s.stakeholder for s in stances]
    normalized = []
    for item in value:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict):
            normalized.append(str(item.get("stakeholder") or item.get("name") or item))
        else:
            normalized.append(str(item))
    return normalized


def _normalize_optional_text(value) -> str | None:
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(str(v) for v in value if v)
    return str(value)


async def classify_item(stances: list[Stance]) -> ClassificationResult:
    item_id = stances[0].item_id if stances else "unknown"
    prompt = "Stances:\n" + "\n".join(s.model_dump_json() for s in stances)
    data = await _llm_classify(prompt)
    return ClassificationResult(
        item_id=item_id,
        status=data["status"],
        summary=_normalize_optional_text(data["summary"]) or "",
        divergence=_normalize_optional_text(data.get("divergence")),
        cited_stances=_normalize_cited_stances(data.get("cited_stances"), stances),
        follow_up=_normalize_optional_text(data.get("follow_up")),
    )
