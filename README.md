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

## Docs

- [Overview](./docs/overview.md)
- [Design Spec](./docs/design-spec.md)
- [Build Plan](./docs/build-plan.md)
- [Pitch Script](./docs/pitch-script.md)

