---
date: 2026-06-06
tags: [project, hackathon, openai, build-plan]
status: active-plan
---

# Build Plan - One-Day Hackathon

## Guiding Principle

Build the smallest thing that proves the product insight:

> A normal summarizer misses fake agreement. Our assumption-diff system catches it.

Do not spend the day proving distributed infrastructure. Spend the day proving the crux engine and showing it clearly.

## Minimum Winning Build

The project is successful if it can demo:

1. A 9-item checkout go/no-go agenda.
2. Four stakeholder agents producing structured stances.
3. A naive baseline that wrongly marks the security item as agreed.
4. An assumption-aware classifier that catches fake agreement.
5. A board that animates **9 -> 2**.
6. A decision record with provenance.
7. A tiny eval suite proving the classifier handles more than the planted case.

Everything else is optional.

## Explicit Cuts

Do not build these unless the minimum winning build is already done:

- cross-laptop MCP join,
- real meeting listener,
- calendar/email integration,
- real auth,
- persistent database,
- multi-room admin features,
- generic meeting import.

## Work Split

| Owner | Workstream | Deliverables |
|---|---|---|
| Wai Chong | Engine + OpenAI agent flow | schemas, persona prompts, stance generation, classifier, baseline, evals, cached fallback |
| Shang | Server + integration | API routes, run orchestration, state assembly, cached/live mode switch |
| JT | Frontend + pitch | board UI, 9->2 animation, assumption diff panel, decision record view, deck/script |

If one stream finishes early, help the engine first, frontend second, server third.

## Timeline

| Time | Block | Goal |
|---|---|---|
| 08:30-09:00 | Kickoff | Confirm scope, create repo, check OpenAI key, choose FastAPI or Node backend |
| 09:00-10:00 | Contract lock | Finalize JSON schemas, agenda items, statuses, and board state shape |
| 10:00-11:30 | Golden data | Write 4 personas, 9 agenda items, KB snippets, expected final classification |
| 11:30-13:00 | Vertical slice v1 | Cached stances -> classifier -> board JSON -> frontend render |
| 13:00-13:30 | Integration checkpoint | Prove one full pass: security fake agreement appears from data, not only hand-coded UI |
| 13:30-15:00 | Real agent pass | Wire OpenAI stance generation and live classification, keep cached fallback |
| 15:00-16:00 | Baseline + evals | Add naive classifier panel and 5 eval cases |
| 16:00-17:00 | Demo board polish | Animation, assumption diff, final decision record, status colors |
| 17:00-18:00 | Freeze | Stop feature work, fix bugs, record fallback video |
| 18:00-20:00 | Rehearse | Run 3-minute pitch repeatedly, prepare Q&A, verify fallback |
| 20:00-21:00 | Buffer | Final polish and submission |

Feature freeze is **17:00**. After that, only demo hardening.

## Data To Build First

### Personas

- **PM:** wants to ship before 11.11 for conversion and promo revenue.
- **Backend:** believes checkout backend is ready and assumes session handling is server-side.
- **SRE:** worried about traffic spikes, queue backpressure, and rollback readiness.
- **Security:** blocks launch if any checkout token is stored client-side.

### Agenda Items

Use 9 items. Recommended shape:

1. Feature scope finalized
2. Payment provider fallback
3. Feature flag rollout
4. Customer support comms
5. Analytics instrumentation
6. Rollback owner
7. Promo freeze timing
8. 11.11 load readiness
9. Checkout token/session security

Expected classifications:

- Items 1-7: `agreed`
- Item 8: `crux`
- Item 9: `fake_agreement`, then treated as meeting crux

## API Shape

Keep the API minimal.

```text
POST /api/demo/reset
POST /api/demo/run-agents
POST /api/demo/classify
GET  /api/demo/board
GET  /api/demo/record
GET  /api/demo/evals
```

If time is tight, collapse this into:

```text
POST /api/demo/run
GET  /api/demo/state
```

## Engine Tasks

### Stance Generation

Each stakeholder agent returns structured JSON:

```json
{
  "stakeholder": "SRE",
  "item_id": "load-readiness",
  "position": "block",
  "rationale": "Checkout has not passed 11.11 traffic simulation.",
  "key_assumptions": ["Traffic may exceed last year's peak by 35%"],
  "confidence": 0.82,
  "evidence_refs": ["kb-load-test-summary"]
}
```

### Naive Baseline

Classifies only from positions:

- all agree or conditionally agree -> `agreed`
- any block -> `crux`

This should fail on the security fake agreement.

### Assumption-Aware Classifier

Classifies from:

- position,
- rationale,
- key assumptions,
- evidence refs.

It must return status, explanation, divergence, and cited stances.

### Eval Suite

Five required cases:

1. true agreement -> `agreed`
2. obvious disagreement -> `crux`
3. same words, different assumptions -> `fake_agreement`
4. different words, same assumption -> `agreed`
5. ambiguous signal -> `needs_clarification`

## Frontend Requirements

Required screens/components:

- room header with decision title,
- **Run pre-meeting agents** button,
- 9-item board,
- compression counter,
- selected item detail panel,
- baseline vs assumption-aware comparison,
- decision record.

Visual behavior:

- 7 items turn green.
- load-readiness remains red.
- security item turns amber with "same words, different meaning."
- security item expands to show assumption diff.
- final counter reads **2 items need meeting**.

## Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| OpenAI calls slow or fail | Medium | Cache stance outputs and final classifications |
| Demo looks staged | High | Show baseline contrast and eval suite |
| Team overbuilds infra | High | Cut MCP/listener; freeze at 17:00 |
| Classifier inconsistent | Medium | Use golden data, structured prompts, deterministic fallback |
| UI not ready | Medium | Render from `data/golden_board.json` before live wiring |
| Pitch unclear | Medium | Lead with fake agreement, not "meeting productivity" |

## Definition Of Done

- [ ] Demo room loads.
- [ ] 9 agenda items render.
- [ ] Run button produces stakeholder stances.
- [ ] Naive baseline marks security item as agreed.
- [ ] Assumption-aware classifier marks security item as fake agreement.
- [ ] Board reaches **9 -> 2**.
- [ ] Decision record renders agreements, cruxes, and evidence.
- [ ] Eval suite passes 5 cases.
- [ ] Cached fallback works with network disabled or API unavailable.
- [ ] 3-minute demo rehearsed at least 3 times.

## Staff-Engineer Check

Before calling it done, ask:

- Is the fake-agreement example visible without verbal explanation?
- Can the demo survive API slowness?
- Does the eval suite prove this is not just the planted case?
- Is every live claim honest?
- Did we avoid infrastructure that does not strengthen the judging story?
