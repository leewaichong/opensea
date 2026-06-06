---
date: 2026-06-06
tags: [project, hackathon, openai, codex, ai-native]
status: active-plan
---

# PerMyLastEmail - Hackathon Overview

## Event

- **Event:** Sea x OpenAI Codex Hackathon, Singapore
- **Date:** 2026-06-06
- **Team:** PerMyLastEmail
- **Members:** Wai Chong, Shang, JT
- **Track direction:** AI-native products and operations

## One-Liner

**PerMyLastEmail is a pre-meeting crux finder that uses managed agents to surface hidden disagreement before humans sit down.**

It turns a 9-item go/no-go agenda into the 2 items that actually need a meeting.

## Product Thesis

Most meetings do not fail because people disagree. They fail because people spend most of the hour discovering where they already agree, while the dangerous disagreement hides behind shared language.

The sharp example:

> Four people say "make checkout secure." A normal summarizer marks that as agreement. But PM and Backend mean "server-side session," while Security means "no client-side token at all."

Same words. Different assumptions. Bad launch decision.

PerMyLastEmail catches this before the meeting and hands the human owner a short fight list:

- what is genuinely agreed,
- what is truly contested,
- where agreement is fake,
- and what needs clarification.

## Final Hackathon Scope

The original plan explored a live distributed decision room where agents join through MCP and participate across laptops. That is interesting, but too much infrastructure for a one-day hackathon.

The final scope is leaner:

1. Use OpenAI managed/SDK-style agents to simulate 4 stakeholder agents.
2. Each agent emits structured stances over 9 agenda items.
3. A crux classifier compares positions and assumptions.
4. A live board shows the agenda compressing from **9 -> 2**.
5. A baseline comparison shows why this is more than summarization.
6. A decision record preserves provenance and logged dissents.

## What We Are Not Building

- No cross-laptop MCP join flow.
- No real email/calendar integration.
- No live meeting transcription.
- No persistent auth system.
- No claim that the system auto-decides.
- No broad "meeting killer" product.

The system tightens meetings. It does not replace judgment.

## Demo Scenario

**Decision:** Should we ship the new checkout flow before the 11.11 promo freeze?

**Stakeholders:**

- PM: wants to ship for promo revenue.
- Backend: believes the implementation is mostly ready.
- SRE: worries about promo-load risk.
- Security: worries about a new token/session path.

**Agenda shape:**

- 9 original agenda items.
- 7 resolve as true agreements.
- 1 remains a clear crux: SRE load risk.
- 1 looks agreed but is fake agreement: "secure checkout."

Final meeting agenda: **2 items**.

## Winning Claim

The demo should make judges think:

> "A summarizer would have missed that. This system caught a bad decision before the meeting."

That is the product.

## Judging Fit

- **Problem framing:** meetings waste time on non-cruxes and hide real disagreement behind shared words.
- **Implementation quality:** structured multi-agent stance generation, assumption-aware classifier, deterministic board, decision record.
- **Depth of thinking:** fake-agreement detection, failure semantics, provenance, human authority.
- **Effective Codex use:** Codex is used to build, test, red-team, and simplify the product rather than just generating code volume.
