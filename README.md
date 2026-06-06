# PerMyLastEmail

Pre-meeting crux finder for the Sea x OpenAI Codex Hackathon.

PerMyLastEmail uses managed/SDK-style OpenAI agents to collect stakeholder stances before a decision meeting, compare the assumptions underneath those stances, and surface only the agenda items that actually need human discussion.

The demo scenario is a go/no-go decision:

> Should we ship the new checkout flow before the 11.11 promo freeze?

The headline demo compresses a 9-item agenda into 2 real cruxes:

- 7 items resolve as genuine agreement.
- 1 item remains an obvious crux: 11.11 load readiness.
- 1 item looks agreed but is actually fake agreement: "secure checkout" means different things to different stakeholders.

## Why It Matters

A normal meeting summarizer would mark "make checkout secure" as agreement because everyone used the same words.

PerMyLastEmail compares the assumptions:

- PM and Backend assume a server-side session.
- Security means no client-side token at all.

Same words, different assumptions. That hidden mismatch becomes one of the two real meeting topics.

## Hackathon Scope

This repo intentionally avoids heavy distributed infrastructure for the first demo. The winning artifact is the reasoning layer:

- four stakeholder agents,
- structured stance outputs,
- naive baseline classifier,
- assumption-aware crux classifier,
- live board showing `9 -> 2`,
- decision record with provenance,
- small eval suite for credibility.

No cross-laptop MCP join, real meeting listener, email integration, or auth system is on the critical path.

## Build Direction Alignment

Primary direction: **AI-Native Products & Operations**.

PerMyLastEmail is not a faster version of an existing meeting note-taker. It changes the operating pattern: stakeholders send agents into a pre-meeting reasoning loop, and humans receive only the unresolved cruxes with provenance.

Secondary fit: **Deep Domain AI** for product launch readiness. The demo models how PM, Backend, SRE, and Security actually reason about a high-stakes release decision.

## Judging Alignment

| Criterion | What the repo/demo should prove |
|---|---|
| Problem & Solution Fit | Go/no-go meetings waste time on settled topics and miss hidden disagreement. Pre-meeting crux extraction is the right intervention. |
| Build Quality | Working board, structured stance outputs, classifier, baseline, evals, deterministic fallback. |
| Insight & Originality | The novel wedge is fake-agreement detection: same words, incompatible assumptions. |
| Real-World Value | Product teams get shorter launch meetings and avoid shipping decisions based on false consensus. |
| Build Direction | AI-native operations workflow that would not be practical without agentic structured reasoning. |
| Use of Codex | Codex is used for planning, scoping, implementation, tests, red-team review, and demo hardening. |

## Hackathon Declaration Template

This is a new public repository created for the hackathon.

Target artifacts to build during the hackathon:

- project docs and build plan,
- agent/persona workflow,
- assumption-aware crux classifier,
- baseline classifier,
- evaluation cases,
- demo board/prototype,
- decision record view.

Existing code or external projects used:

- none declared yet.

Update this section before final submission so it accurately states what was actually built during the hackathon and what starter code or open-source libraries were used.

## Docs

- [Overview](./docs/overview.md)
- [Design Spec v2 — Slack-native](./docs/design-spec-slack.md) (current direction)
- [Design Spec v1 — web app](./docs/design-spec.md) (superseded)
- [Build Plan](./docs/build-plan.md)
- [Pitch Script](./docs/pitch-script.md)
- [Judging Alignment](./docs/judging-alignment.md)
- [Submission Checklist](./docs/submission-checklist.md)
