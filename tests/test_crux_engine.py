from pmle.schemas import Stance
from pmle.crux_engine import naive_baseline


def _stance(stakeholder, position, assumptions):
    return Stance(stakeholder=stakeholder, item_id="i", position=position,
                  rationale="r", key_assumptions=assumptions, confidence=0.8)


def test_baseline_all_support_is_agreed():
    stances = [_stance("PM", "support", ["server-side session"]),
               _stance("Security", "support", ["no client token"])]
    assert naive_baseline(stances).status == "agreed"  # baseline ignores assumptions -> WRONG on purpose


def test_baseline_any_block_is_crux():
    stances = [_stance("PM", "support", []), _stance("SRE", "block", [])]
    assert naive_baseline(stances).status == "crux"


import pytest
from pmle.crux_engine import classify_item


@pytest.mark.asyncio
async def test_fake_agreement_detected_with_stub(monkeypatch):
    # Stub the LLM call so the eval is deterministic and offline.
    async def fake_llm(prompt: str) -> dict:
        return {"status": "fake_agreement",
                "summary": "Same words, different assumptions.",
                "divergence": "PM: server-side session; Security: no client token",
                "cited_stances": ["PM", "Security"], "follow_up": "Confirm token storage."}
    monkeypatch.setattr("pmle.crux_engine._llm_classify", fake_llm)

    stances = [_stance("PM", "support", ["server-side session"]),
               _stance("Security", "support", ["no client-side token"])]
    result = await classify_item(stances)
    assert result.status == "fake_agreement"
    assert "token" in result.divergence
