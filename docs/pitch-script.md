---
date: 2026-06-06
tags: [project, hackathon, openai, codex, slack, pitch]
status: active-plan
---

# Pitch Script — 6-Minute Demo

PerMyLastEmail is a **Slack-native pre-meeting crux finder**. Every person has a
persistent personal agent in Slack. When a meeting is called, a transient orchestrator
agent reaches out to each person's agent, compares the assumptions under their stances,
clears what it can before anyone sits down, and hands humans only the disagreements that
actually need a meeting.

## Cold Open

> "Four people said: make checkout secure. A summarizer would mark that as agreement. But
> PM and Backend meant a server-side session, while Security meant no client-side token at
> all. Same words, different assumptions — that is how a team accidentally ships the wrong
> design into 11.11."

> "PerMyLastEmail lives in Slack. Everyone already has a personal agent there. When a
> meeting is called, an orchestrator agent quietly talks to everyone's agent, resolves what
> it can, and gives the humans only the fights that matter."

## What's Actually Running

> "Each person has a **persistent managed agent session** — enterprise style: everyone has
> a standing agent that knows their context. The **orchestrator is a transient session**
> spun up for one meeting; it reaches every participant agent, runs the assumption-diff
> classifier, and then dissolves. The agent-to-agent call graph is right there in the
> OpenAI trace viewer."

## Demo Storyboard

| Beat | Time | On Screen | Narration |
|---|---:|---|---|
| 1. Set your stance | 50s | Slack DM with your own agent | "I tell my agent, in plain Slack: 'I'm fine shipping, but only if no checkout token is ever stored client-side.' My agent maps that onto a structured stance. Stances are grounded in what people actually said — not made up." |
| 2. Call the meeting | 35s | `/premeeting` posts the decision + 9-item agenda + action items | "The organizer calls the pre-meeting in Slack. A transient orchestrator spins up." |
| 3. Agents reach out | 60s | OpenAI trace viewer: orchestrator → each participant agent | "The orchestrator queries every participant's persistent agent, item by item. This is real agent-to-agent reasoning — you can watch the call graph live in the trace." |
| 4. The easy 7 dissolve | 35s | Digest: 7 items agreed | "Seven items are genuine agreement. They never reach the meeting." |
| 5. Action items pre-cleared | 35s | Digest: action items resolved / needs-owner | "Resolvable action items get closed before the meeting too — rollback owner assigned, one load-test item flagged because no agent could own it without a human." |
| 6. The real crux | 30s | Load-readiness stays red | "One real disagreement: SRE is not comfortable with 11.11 traffic readiness." |
| 7. Fake agreement caught | 75s | Security item amber → assumption diff | "Here's the important one. Everyone said 'secure checkout,' so a naive baseline says agreed. But the assumption-aware classifier catches the mismatch: PM/Backend assume a server-side session; Security means no client-side token. The orchestrator wasn't sure, so it DM'd the human, the human confirmed, and it locked as a crux." |
| 8. The result | 30s | Digest: 9 → 2 + decision record | "The meeting is now 2 items, not 9 — with provenance and dissents preserved. The human owner still decides." |
| 9. Codex close | 30s | Commit trail, evals, trace | "We used OpenAI Agents SDK for the persistent and transient agents, Slack as the human membrane, and Codex to build, test, and red-team the crux engine." |

## The Main Line

> "We are not summarizing the meeting after it happens. We are preventing the wrong meeting
> from happening — inside the tool the team already lives in."

## Judging Criteria Beats

Make these explicit during the 6 minutes:

- **Problem & Solution Fit:** the 11.11 launch go/no-go is a real cross-functional meeting; most of the hour is spent re-discovering agreement.
- **Build Quality:** persistent + transient managed agents, conversational stance editing, assumption-aware classifier, naive baseline, action-item clearing, Slack digest, evals, cached fallback — all working.
- **Insight & Originality:** fake-agreement detection is the wedge; the baseline proves it's not summarization.
- **Real-World Value:** shorter meetings, fewer false-consensus launch decisions, action items closed before anyone meets — all in Slack, no new tool to adopt.
- **Build Direction (AI-native operations):** the operating pattern changes — people send agents into a pre-meeting reasoning loop; humans receive only unresolved cruxes with provenance.
- **Use of Codex:** Codex scoped the pivot, built the engine and orchestrator, wrote the evals, and red-teamed the classifier.

## Why Slack, Why Persistent vs Transient

> "Slack is where the team already is, so adoption cost is zero. The persistent agents are
> the enterprise reality — everyone gets a standing agent. The orchestrator is transient on
> purpose: it exists only for the meeting, holds no standing authority, and dissolves when
> it's done. It compresses *what to discuss*; it never makes the business decision."

## What Is Live vs Cached

> "Stances can be cached for stage timing, but the assumption-diff classification runs live
> on those structured stances, and we keep a deterministic fallback so stage timing never
> decides the demo. The core claim isn't about API speed — it's that position-only
> classification misses fake agreement while assumption-aware classification catches it.
> That's what the baseline and evals show."

## Judge Q&A

### "Isn't this just a meeting summarizer?"

No. Summarizers act after the meeting. PerMyLastEmail acts before it, in Slack, and catches
hidden disagreement a transcript summary would flatten.

### "How do you know the agents aren't just making the stances up?"

Stances are set by the humans, conversationally, through their own agents. Every stance
traces back to something a person actually told their agent — and the human can revise it
any time. That's why we can trust the compression.

### "How do you know it isn't staged?"

Three things: the naive baseline fails on the security item; the assumption diff explains
exactly why; and the eval suite includes a false-positive trap where different wording with
the same assumption still classifies as agreed.

### "Do agents decide for humans?"

No. The orchestrator compresses the agenda. The human owner decides, with provenance, and
can pull any compressed item back into the meeting.

### "Do agents leak private context?"

No raw private context is shared between agents. They emit structured stances: position,
rationale, assumptions, confidence, evidence references.

### "Why managed agents / OpenAI?"

We need persistent per-person sessions, transient orchestration, agent-to-agent tool calls,
and built-in tracing — the Agents SDK gives all four out of the box, so we spent our day on
the product logic: comparing assumptions and extracting cruxes.

## Backup Lines

If Slack is slow or flaky:

> "I'll switch to the cached path — same orchestrator, same digest, no network dependency."

If the trace is the only thing live:

> "The trace viewer is the durable proof: that's the real orchestrator-to-agent call graph
> from this run."

## Closing

> "Meetings don't fail because people disagree. They fail because people think they agree.
> PerMyLastEmail catches that before the hour is gone — right inside Slack."
