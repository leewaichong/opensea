import asyncio
import os
from pmle import orchestrator
from pmle.data.cached_stances import CACHED
from pmle.digest import render_text
from pmle.schemas import ClassificationResult, Stance

_CACHE = {(s.stakeholder, s.item_id): s for s in CACHED}


async def _offline_ask(person, item_id, item_text):
    return _CACHE.get((person, item_id)) or Stance(
        stakeholder=person,
        item_id=item_id,
        position="support",
        rationale="No known blocker.",
        key_assumptions=[],
    )


async def _offline_classify(stances):
    item = stances[0].item_id
    if item == "security":
        return ClassificationResult(
            item_id=item,
            status="fake_agreement",
            summary="All agree on secure checkout, but assumptions differ.",
            divergence="PM/Backend: server-side session; Security: no client-side token storage",
            cited_stances=["PM", "Backend", "Security"],
            follow_up="Confirm whether any checkout token is stored client-side.",
        )
    if any(s.position == "block" for s in stances):
        return ClassificationResult(
            item_id=item,
            status="crux",
            summary="SRE blocks until 11.11 load readiness is proven.",
            divergence="SRE needs traffic simulation before launch.",
            cited_stances=["SRE", "PM"],
        )
    return ClassificationResult(
        item_id=item,
        status="agreed",
        summary="No blocking divergence found.",
        cited_stances=[s.stakeholder for s in stances],
    )

async def main():
    if not os.environ.get("OPENAI_API_KEY"):
        orchestrator.ask_stance = _offline_ask
        orchestrator.classify_item = _offline_classify
    board = await orchestrator.run_meeting()
    print(render_text(board))

if __name__ == "__main__":
    asyncio.run(main())
