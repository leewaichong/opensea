---
date: 2026-06-06
tags: [project, hackathon, judging]
status: active-plan
---

# Judging Alignment

This document maps PerMyLastEmail directly to the hackathon criteria so the team builds what judges are looking for.

## Slide-Derived Constraints

- The product is judged more than the pitch.
- Presentation format is **6 min demo / pitch** plus **2 min Q&A**.
- Submission deadline is **5:00 PM sharp**.
- Submission requires a GitHub repo, project writeup, optional demo link, and declarations.
- README/submission must state what was built during the hackathon.
- If existing code is used, the existing repo must be linked and the new hackathon-built work must be significant and clear.

## Criteria Map

| Judging Criterion | What To Show | Repo/Demo Evidence |
|---|---|---|
| Problem & Solution Fit | Launch go/no-go meetings waste time and hide real disagreement. | 11.11 checkout scenario, 9-item agenda, 9 -> 2 compression. |
| Build Quality | The product works under demo conditions and has fallbacks. | Working board, cached stances, live/cached classification switch, evals, deterministic fallback. |
| Insight & Originality | The core idea is fake-agreement detection, not generic summarization. | Baseline says "agreed"; assumption-aware classifier catches incompatible assumptions. |
| Real-World Value | Product teams avoid bad release decisions and shorter meetings become possible. | Decision record, evidence refs, final 2-item fight list. |
| Alignment With Build Direction | AI-native operations workflow that changes how teams prepare for decisions. | Managed agents represent stakeholder roles and produce structured stances before a meeting. |
| Use of Codex | Codex materially shaped and built the product. | Commit trail, docs, tests/evals, red-team notes, generated scaffolding. |

## Reviewer-Facing README Requirements

The README should make these obvious without requiring the judges to inspect every file:

1. What the product does.
2. Why it is not a meeting summarizer.
3. Which build direction it aligns with.
4. What was built during the hackathon.
5. What existing code, if any, was used.
6. How Codex was used.
7. How to run the demo once the app exists.

## Demo Must-Haves

The 6-minute demo should include:

1. Problem setup: 11.11 checkout go/no-go.
2. Four managed stakeholder agents producing stances.
3. Board compression from 9 items to 2.
4. Naive baseline incorrectly marking the security item as agreed.
5. Assumption-diff panel showing the hidden security mismatch.
6. Decision record with human owner and provenance.
7. Eval suite or eval output proving this is not one planted case.
8. Codex usage story grounded in actual artifacts.

## Q&A Prep

### "Why is this not just summarization?"

Summarizers compress text after a meeting. PerMyLastEmail changes the pre-meeting workflow by detecting whether apparent agreement is real before humans spend the hour.

### "How do we know this is not staged?"

Show the baseline, assumption diff, and eval cases. The false-positive trap matters: different wording with the same assumption should still classify as agreement.

### "Who benefits?"

Product launch teams, incident-review owners, policy/risk reviewers, and any cross-functional group that needs an auditable go/no-go decision.

### "What did Codex do?"

Codex helped simplify the architecture, draft specs, generate implementation scaffolding, create test/eval cases, review risk, and tighten the demo story.

