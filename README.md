# PerMyLastEmail

A **Slack-native pre-meeting crux finder** for the Sea x OpenAI Codex Hackathon.

Every person has a persistent personal agent in Slack. When a meeting is called, a
transient **orchestrator** agent coordinates those participant agents, compares the
*assumptions* underneath their stances, clears what can be handled asynchronously, and
hands humans only the disagreements that actually need a meeting.

## Why It Matters

Meetings often get scheduled because the team has not separated real disagreement from
surface-level alignment. People may use the same words while relying on different
assumptions, success criteria, risk thresholds, or ownership expectations.

PerMyLastEmail catches that before the meeting. It lets participant agents maintain each
person's current stance, then has an orchestrator agent compare those structured stances
for genuine agreement, unresolved cruxes, fake agreement, and missing context.

## How It Works

- **Persistent participant agents** — each person has an OpenAI Agents SDK session
  (`SQLiteSession`) that holds their context and owns a structured stance contract.
  People update those stances by chatting naturally with their agent in Slack.
- **Transient orchestrator agent** — spun up per meeting; queries participant agents,
  compares their stances and assumptions, resolves what it can, escalates ambiguous gaps
  back to humans, posts the digest, then dissolves.
- **Structured stance exchange** — agents coordinate through explicit `Stance`,
  `ClassificationResult`, and `ActionItem` contracts instead of unstructured summaries.
- **Reasoning view** — the agent-to-agent coordination path is visible in the OpenAI
  Dashboard trace viewer through built-in tracing.
- **Slack as the human membrane** — people stay in the tool they already use while agents
  coordinate the pre-meeting reasoning loop behind it.

## Agent Coordination

PerMyLastEmail is built around a managed-agent pattern:

1. A human updates their position in Slack.
2. Their persistent participant agent maps that conversation onto a structured stance:
   position, rationale, assumptions, confidence, and evidence.
3. A meeting creator starts a pre-meeting pass.
4. The transient orchestrator asks each participant agent for the current stance on each
   item.
5. The orchestrator classifies items as agreed, cruxes, fake agreement, or needing
   clarification.
6. If a gap needs human input, the orchestrator routes the question back through Slack,
   waits for the stance to be updated, and re-runs the classification.
7. The final digest gives humans the narrowed meeting agenda, provenance, and remaining
   decisions.

The important product shift is that humans are not asked to fill out another form or
read another dashboard. They talk to their agents conversationally; the agents maintain
the structured state required for reliable coordination.

## Build Direction

Primary: **AI-Native Products & Operations**. PerMyLastEmail changes the operating
pattern — people send agents into a pre-meeting reasoning loop, and humans receive only
the unresolved cruxes with provenance.

Secondary: **Deep Domain AI** for operational decision-making, where different roles
often reason from different private constraints and assumptions.

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

Codex was used as a coding agent throughout the project, not just as a code generator.
It helped shape the product direction, review the Slack-native managed-agent
architecture, decompose the implementation into parallel workstreams, generate and
iterate on code, write tests, inspect failures, red-team the classifier behavior, review
the scripts and setup path, and refine documentation.

That workflow matters to the build: Codex acted as an engineering collaborator that could
move between product framing, architecture, implementation, test design, debugging, and
documentation while keeping the repository state visible.

## Docs

- [Design Spec — Slack-native](./docs/design-spec-slack.md)
- [Build Plan — implementation tasks](./docs/build-plan-slack.md)
- [Pitch Script](./docs/pitch-script.md)
