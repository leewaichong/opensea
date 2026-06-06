---
date: 2026-06-06
tags: [project, hackathon, openai, design-spec]
status: active-plan
---

# Design Spec - Managed-Agent Crux Finder

## Product Shape

PerMyLastEmail is a single web app that runs a pre-meeting decision simulation.

The user creates a decision room, runs stakeholder agents, watches a board compress the agenda, and receives a decision record.

The app is intentionally not a distributed meeting platform. The "room" is the product UI. Managed agents do the stakeholder work behind the scenes.

## Core User Flow

1. Organizer creates a room from a fixed demo brief:
   "Go/no-go: ship new checkout before 11.11 freeze."
2. App loads 4 stakeholder personas and 9 agenda items.
3. User clicks **Run pre-meeting agents**.
4. Four agents produce structured stances for all agenda items.
5. Crux classifier compares stances and assumptions per item.
6. Board animates:
   - 7 items resolve green,
   - 1 SRE load item stays red,
   - 1 "secure checkout" item turns amber, shows assumption diff, then locks red.
7. App shows a decision record with agreements, cruxes, fake agreement, evidence, and next steps.

## Architecture

Use the smallest architecture that can demo the insight clearly.

```text
web/
  React board, controls, baseline panel, decision record

server/
  API routes, OpenAI calls, cached fallback, board-state assembly

engine/
  schemas, classifier prompt, baseline classifier, evaluation tests

data/
  personas, agenda, knowledge base, cached stances, golden board result
```

Recommended stack:

- **Frontend:** Vite + React + Tailwind
- **Backend:** FastAPI or lightweight Node/Express
- **AI:** OpenAI Responses API / Agents SDK style orchestration
- **State:** in-memory JSON for hackathon demo
- **Fallback:** cached stance JSON and cached board JSON

## Agent Design

There are 5 logical agents:

1. **PM Agent**
2. **Backend Agent**
3. **SRE Agent**
4. **Security Agent**
5. **Crux Judge Agent**

The first 4 agents receive:

- public meeting brief,
- their private stakeholder context,
- agenda items,
- small knowledge base.

They output one structured stance per agenda item.

The Crux Judge Agent receives all stances for an item and classifies the item.

## Data Contracts

### Meeting

```json
{
  "id": "demo-1111-checkout",
  "title": "Ship new checkout before 11.11 freeze?",
  "owner": "PM",
  "decision_rule": "owner_call_with_logged_dissents",
  "stakeholders": ["PM", "Backend", "SRE", "Security"],
  "agenda_items": []
}
```

### Agenda Item

```json
{
  "id": "security-token-path",
  "text": "Confirm checkout security posture",
  "status": "open",
  "compression_count": 9,
  "divergence": null,
  "stances": {}
}
```

Allowed statuses:

- `open`
- `agreed`
- `fake_agreement`
- `crux`
- `needs_clarification`

### Stance

```json
{
  "stakeholder": "Security",
  "item_id": "security-token-path",
  "position": "agree_with_condition",
  "rationale": "Checkout can ship only if no token is stored client-side.",
  "key_assumptions": [
    "No client-side token storage",
    "Session state remains server-controlled"
  ],
  "confidence": 0.86,
  "evidence_refs": ["kb-security-incident-2025"]
}
```

### Classification Result

```json
{
  "item_id": "security-token-path",
  "status": "fake_agreement",
  "summary": "All stakeholders agree on 'secure checkout', but PM/Backend assume server-side session while Security means no client-side token at all.",
  "divergence": "PM/Backend: server-side session; Security: no client-side token",
  "cited_stances": ["PM", "Backend", "Security"],
  "follow_up": "Confirm whether the implementation stores any checkout token client-side."
}
```

## Classifier Semantics

The classifier must use position and assumptions, not position alone.

### `agreed`

Positions align and assumptions align.

Example: everyone agrees feature flags are enabled and all mean the same rollout guardrail.

### `crux`

Positions diverge in a way that affects the go/no-go decision.

Example: SRE says launch load risk is unacceptable for 11.11.

### `fake_agreement`

Surface wording aligns but assumptions conflict.

Example: everyone says "secure," but stakeholders mean incompatible security designs.

### `needs_clarification`

Evidence is too thin or assumptions are ambiguous. The engine refuses to guess.

This is a credibility feature. The system should admit uncertainty instead of inventing agreement.

## Baseline Classifier

Show a naive baseline:

- Looks only at stakeholder positions.
- Calls the "secure checkout" item agreed.

Then show the assumption-aware classifier:

- Extracts assumptions.
- Detects mismatch.
- Marks it as fake agreement.

This side-by-side is the proof that the product is not just summarization.

## Board Behavior

The board is the demo's main surface.

Required states:

- Grey: open
- Green: agreed
- Amber: fake agreement
- Red: crux
- Blue/neutral: needs clarification

The compression counter is owned by the classifier result, not derived by counting colors in the UI.

Counter semantics:

```text
compression_count = number of items still requiring human meeting attention
```

The final result should be:

```text
9 original items
7 agreed
1 crux
1 fake agreement promoted to crux
= 2 meeting items
```

The fake-agreement tile should never turn green. It should move:

```text
open -> fake_agreement -> crux
```

## Decision Record

The final record should include:

- resolved agreements,
- remaining cruxes,
- surfaced fake agreement,
- dissents or conditions,
- evidence references,
- suggested meeting agenda,
- human decision owner.

Example close:

```text
Decision owner: PM
Rule: owner call with logged dissents
Resolved async: 7/9 items
Meeting agenda:
1. Promo load readiness under 11.11 traffic
2. Checkout token/session security design
```

## Trust Boundary

Agents do not share raw private context with each other.

They emit structured stances:

- position,
- rationale,
- key assumptions,
- confidence,
- evidence references.

The human owner can inspect provenance and override any compression.

The product compresses what to discuss. It does not finalize the business decision.

## Demo Honesty

For reliability:

- stakeholder stances may be cached,
- board playback may be deterministic,
- classifier can run live on cached stances,
- fallback classification can be available for stage safety.

Suggested judge answer:

> "The stakeholder responses are cached for timing. The assumption-diff classification you see is running live on those stances. We also have deterministic fallback output so the demo does not depend on network timing."
