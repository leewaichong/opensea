---
date: 2026-06-06
tags: [project, hackathon, openai, codex, slack, design-spec]
status: active-plan
supersedes: design-spec.md
---

# Design Spec v2 — Slack-Native Managed-Agent Crux Finder

This supersedes the v1 single-web-app design ([design-spec.md](./design-spec.md)).
The product insight is unchanged — **catch fake agreement before the meeting** — but
the surface and architecture pivot to a real Slack-native, managed-agent system.

## What Changed From v1

| | v1 (web app) | v2 (Slack-native) |
|---|---|---|
| Surface | Custom React board | Slack (human membrane) + OpenAI trace viewer (reasoning view) |
| Agents | Simulated in one backend | Real OpenAI Agents SDK managed sessions |
| Participant agents | Stateless persona prompts | **Persistent** sessions (`SQLiteSession` per person) — enterprise "everyone has a standing agent" |
| Orchestrator | Classifier function | **Transient** managed agent session, dies when meeting ends |
| Agent-to-agent | N/A | Orchestrator queries participants via `agent.as_tool()` |
| Observability | N/A | Built-in SDK tracing → OpenAI Dashboard Trace viewer (free) |

The crux engine (assumption-aware classifier + naive baseline) carries over unchanged
as the reasoning payload.

## Product Shape

PerMyLastEmail runs a **pre-meeting reasoning loop** inside Slack.

A meeting creator drops a decision, agenda, action items, and participants into Slack.
A transient **orchestrator** agent spins up, reaches out to each participant's
**persistent personal agent**, collects structured stances, compares the *assumptions*
underneath them, resolves everything resolvable, escalates the one real gap to a human
via Slack DM, and posts back a compressed agenda + decision record. Then it dissolves.

Slack is purely the **human membrane**: people talk to their own standing agent; the
orchestrator works behind it. The "everyone has their own agent" model lives in
**persistent per-person sessions**, multiplexed behind a single Slack bot for the demo
(production = one bot per person).

## Architecture

```text
SLACK  (human membrane — one app, one bot)
  creator message/slash command: decision + 9 agenda items + action items + participants
  bot DMs the human for the one real gap, relays the reply
  orchestrator digest posted back to the meeting channel/thread

BACKEND  (Python · OpenAI Agents SDK + Slack Bolt / Socket Mode)
  participant agents : Agent(persona) + SQLiteSession(person_id)   ← PERSISTENT
                       hold private context/knowledge
                       own a structured Stance store (the data contract)
                       read/write tools → human conversation mutates the contract
                       exposed via .as_tool() → return current Stance(s)
  orchestrator agent : transient Agent per meeting
                       tools = [each participant.as_tool()] + crux_engine
                       per item: query all → compare stances+assumptions → classify
                                 → escalate gaps to Slack DM → assemble digest
                       session discarded when meeting ends
  crux engine        : assumption-aware classifier + naive baseline (the contrast)
  observability      : SDK tracing → OpenAI Dashboard Trace viewer (the reasoning view)

PERSISTENCE
  one SQLite memory file per participant (survives meetings)
  orchestrator session ephemeral
```

Stack:
- **Agents:** OpenAI Agents SDK (Python), persistent `SQLiteSession`, agents-as-tools.
- **Slack:** Slack Bolt for Python, **Socket Mode** (no public URL / no ngrok).
- **Reasoning view:** OpenAI Dashboard Trace viewer (built-in, on by default).
- **State:** SQLite session files; cached stance JSON for fallback.

## Agents

5 logical agents, same roles as v1:

1. **PM Agent** — persistent
2. **Backend Agent** — persistent
3. **SRE Agent** — persistent
4. **Security Agent** — persistent
5. **Orchestrator** — transient, per meeting

Each participant agent receives: public brief, its private stakeholder context, agenda
items, small KB. It returns **one structured Stance per agenda item**. The orchestrator
calls each participant as a tool, aggregates, and classifies.

## Data Contracts

Carried over from v1 (unchanged). The `Stance` and `Classification Result` schemas in
[design-spec.md](./design-spec.md) remain authoritative.

### Stance (per item, per participant)

```json
{
  "stakeholder": "Security",
  "item_id": "security-token-path",
  "position": "agree_with_condition",
  "rationale": "Checkout can ship only if no token is stored client-side.",
  "key_assumptions": ["No client-side token storage", "Session stays server-controlled"],
  "confidence": 0.86,
  "evidence_refs": ["kb-security-incident-2025"]
}
```

### Classification Result (per item, from orchestrator + crux engine)

```json
{
  "item_id": "security-token-path",
  "status": "fake_agreement",
  "summary": "All agree on 'secure checkout', but PM/Backend assume server-side session while Security means no client-side token at all.",
  "divergence": "PM/Backend: server-side session; Security: no client-side token",
  "cited_stances": ["PM", "Backend", "Security"],
  "follow_up": "Confirm whether the implementation stores any checkout token client-side."
}
```

Statuses: `open`, `agreed`, `fake_agreement`, `crux`, `needs_clarification`.

### Action Item (first-class — the "clear it before the meeting" half)

```json
{
  "id": "ai-rollback-owner",
  "text": "Assign a rollback owner for the 11.11 launch",
  "status": "resolved",
  "resolution": "Backend agent confirmed SRE owns rollback; SRE agent agreed.",
  "owner": "SRE",
  "resolved_by": ["Backend", "SRE"]
}
```

Action-item statuses: `open`, `resolved` (agents reached closure async),
`reassigned` (owner changed), `needs_owner` (no one claimed it — goes to the meeting).
The orchestrator attempts to clear each action item by querying the relevant agents,
exactly like agenda items, and reports the outcome as its own digest beat.

## Conversational Contract Editing

The Stance contract is **owned by the human, edited through their agent.** A person DMs
their persistent agent in Slack to **set, update, or change** any field of their stance —
position, rationale, key assumptions, confidence, evidence. The agent maps free-form
natural language onto the structured `Stance` schema and writes it to its store, then
confirms back.

```text
Human (Slack DM): "On the security item — I'm fine shipping, but only if no checkout
                   token is ever stored client-side. That's a hard condition."
Agent:            maps → Stance{position: agree_with_condition,
                                 key_assumptions: ["No client-side token storage"], ...}
                  writes to store → "Got it. Updated your security stance: conditional
                  approval, hard requirement = no client-side token. Anything else?"
```

This means:
- Stances are **grounded in what the human actually said**, not persona hallucination —
  a direct answer to "how do we know this isn't staged / made up?"
- The persistent session accumulates the human's positions across meetings; they can
  revise at any time and the agent re-versions the contract.
- The orchestrator always reads the **current** contract state when it runs.

Agent tools: `get_stance(item_id)`, `set_stance(item_id, fields)`,
`update_stance(item_id, partial_fields)`. The human's input is conversational; the
mapping to structured fields is the agent's job.

## Orchestration Flow

0. (Ongoing) Humans converse with their agents in Slack to **set/update** their stances —
   the data contract is populated by real human input, not persona guesswork.
1. Human creator posts the brief in Slack (decision + 9 items + action items + participants).
2. Slack handler spins up a transient orchestrator session.
3. For each agenda item, orchestrator calls each participant agent (as a tool) → reads its
   **current** Stance from the contract store.
4. Crux engine classifies each item from position **and** assumptions.
5. When a stance is missing/ambiguous (`needs_clarification`) → the orchestrator asks that
   participant's agent to fill the gap, which **DMs the human** to set the field
   conversationally, then re-runs the item with the updated contract.
6. Orchestrator clears resolvable **action items** the same way (query relevant agents →
   `resolved` / `reassigned` / `needs_owner`).
7. Orchestrator assembles the digest and posts it back to the meeting channel:
   - **Agenda compression:** `9 → 2` with the two real cruxes.
   - **Action items pre-cleared:** e.g. "3 resolved, 1 reassigned, 1 needs an owner."
   - **Decision record:** provenance, dissents, owner.
   Session is discarded.
8. Judges can open the OpenAI Trace viewer to see the agent-to-agent call graph.

## The Human-in-the-Loop Moment (demo)

The conversational editing above is the human membrane in action. For the demo, the
planted beat is: the orchestrator hits a `needs_clarification` on the security item →
the Security agent DMs its human ("does the implementation store any checkout token
client-side?") → the human answers conversationally → the agent updates the Stance →
the crux is confirmed. Same mechanism as setup-time editing, surfaced live on stage.

## Baseline Contrast (unchanged — the proof)

- **Naive baseline:** positions only → marks "secure checkout" as `agreed` (wrong).
- **Assumption-aware:** extracts assumptions → catches the mismatch → `fake_agreement`.

This side-by-side proves the product is not summarization.

## Demo Scenario (reused)

**Decision:** Ship new checkout before the 11.11 promo freeze?
**Participants:** PM, Backend, SRE, Security. **9 agenda items.**

Expected outcome:
- 7 items → `agreed` (pre-cleared, incl. resolvable action items)
- 1 item → `crux` (SRE: 11.11 load readiness)
- 1 item → `fake_agreement` → promoted to crux (security token path)
- **Final meeting agenda: 2 items.** `9 → 2`.

## Build Sequence (~5 hrs, feature freeze 16:00, submit 17:00)

| Owner | Workstream | Deliverables |
|---|---|---|
| Wai Chong | Orchestrator + crux engine | orchestrator agent, agents-as-tools wiring, stance schema, assumption-aware classifier, naive baseline, 5 evals |
| Shang | Participant agents + persistence | 4 persona agents, persistent `SQLiteSession` per person, structured Stance store + `get/set/update_stance` tools (conversational contract editing), private-knowledge data, cached-stance fallback |
| JT | Slack integration + pitch | Bolt Socket Mode app, brief intake, **human↔agent DM conversation routing**, DM escalation, Block Kit digest, demo run, 6-min deck |

Integration milestone: one full pass where the security `fake_agreement` appears from
real agent stances (not hand-coded), digest posts to Slack, trace shows the call graph.

## Fallbacks / Risk

| Risk | Mitigation |
|---|---|
| OpenAI calls slow/fail | Cached stance JSON; deterministic digest |
| Slack setup eats time | One app, Socket Mode (no ngrok), single bot |
| Live demo flaky | Trace viewer is the durable "wow"; cached path posts the same digest |
| Overbuild | One bot, one human, one planted escalation; freeze 16:00 |

## Honesty Line

> "Each person has a persistent managed agent session — enterprise style, everyone has a
> standing agent. The orchestrator is a transient managed session that queries them and
> dissolves. Stances can be cached for stage timing, but the assumption-diff
> classification runs live, and the agent-to-agent call graph is right there in the
> OpenAI trace viewer."

## Out Of Scope (still cut)

- One Slack bot per person (production shape, not demo).
- Real calendar/email integration.
- Live meeting transcription.
- Persistent DB beyond SQLite session files.
- Auto-deciding the business decision — the human owner still decides.
