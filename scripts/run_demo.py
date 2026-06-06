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
    if item == "objective":
        return ClassificationResult(
            item_id=item,
            status="fake_agreement",
            summary="Everyone says younger shoppers, but success criteria differ.",
            divergence="Growth: acquisition and app installs; Commerce: GMV and voucher redemption; Campaign Lead: mainstream-safe youth reach",
            cited_stances=["Wai Chong", "Shang", "John Taylor"],
            follow_up="Decide whether the primary objective is acquisition, GMV, or brand reach.",
        )
    if item == "role-mix":
        return ClassificationResult(
            item_id=item,
            status="crux",
            summary="The creator role split is unresolved.",
            divergence="Wai Chong prefers Mika as hero face; Shang requires Jayden for Shopee Live conversion; John may split hero and conversion roles.",
            cited_stances=["Wai Chong", "Shang", "John Taylor"],
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
