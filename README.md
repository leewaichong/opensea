# PerMyLastEmail

A **Slack-native pre-meeting crux finder** for the Sea x OpenAI Codex Hackathon.

Every person has a persistent personal agent in Slack. When a meeting is called, a
transient **orchestrator** agent reaches out to each participant's agent, compares the
*assumptions* underneath their stances, clears what it can before anyone sits down, and
hands humans only the disagreements that actually need a meeting.

The demo scenario is a go/no-go decision:

> Should we ship the new checkout flow before the 11.11 promo freeze?

It compresses a 9-item agenda into **2 real cruxes**:

- 7 items resolve as genuine agreement.
- 1 item stays a clear crux: 11.11 load readiness.
- 1 item looks agreed but is **fake agreement**: "secure checkout" means different things to different stakeholders.

Resolvable **action items** are pre-cleared in the same pass.

## Why It Matters

A normal meeting summarizer marks "make checkout secure" as agreement because everyone
used the same words. PerMyLastEmail compares the assumptions underneath:

- PM and Backend assume a **server-side session**.
- Security means **no client-side token at all**.

Same words, different assumptions. That hidden mismatch becomes one of the two real
meeting topics — caught before the meeting, inside the tool the team already uses.

## How It Works

- **Persistent participant agents** — each person has an OpenAI Agents SDK session
  (`SQLiteSession`) that holds their context and a structured stance contract. People
  set and update their stances by chatting with their agent in Slack.
- **Transient orchestrator** — spun up per meeting; queries each participant agent via
  agents-as-tools, runs the assumption-aware crux engine, escalates the one real gap to a
  human via Slack DM, posts the digest, then dissolves.
- **Reasoning view** — the agent-to-agent call graph is visible in the OpenAI Dashboard
  trace viewer (built-in tracing), no custom dashboard needed.
- **Slack** is the human membrane; no new tool to adopt.

## Build Direction

Primary: **AI-Native Products & Operations**. PerMyLastEmail changes the operating
pattern — people send agents into a pre-meeting reasoning loop, and humans receive only
the unresolved cruxes with provenance.

Secondary: **Deep Domain AI** for product-launch readiness (how PM, Backend, SRE, and
Security actually reason about a high-stakes release).

## Built During The Hackathon

This is a new public repository created for the Sea x OpenAI Codex Hackathon.

- Slack-native managed-agent architecture (persistent participant agents + transient orchestrator)
- conversational stance/contract editing
- assumption-aware crux classifier + naive baseline
- action-item pre-clearing
- evaluation cases and cached/offline fallback
- Slack Socket Mode app and digest

Existing OSS used: standard framework/library dependencies only (OpenAI Agents SDK,
Slack Bolt, pydantic).

## Use of Codex

Codex scoped the Slack pivot, built the crux engine and orchestrator, wrote the evals,
and red-teamed the classifier — visible in the commit trail, tests, and design docs.

## Docs

- [Design Spec — Slack-native](./docs/design-spec-slack.md)
- [Build Plan — implementation tasks](./docs/build-plan-slack.md)
- [Pitch Script](./docs/pitch-script.md)
