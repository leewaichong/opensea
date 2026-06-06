---
date: 2026-06-06
tags: [project, hackathon, openai, codex, slack, pitch]
status: active-plan
---

# Pitch Script — 6-Minute Demo

PerMyLastEmail is a **Slack-native pre-meeting crux finder**. The Slack bot is named
**Mochi**. Every participant has a persistent personal agent. When someone asks Mochi to
prep a meeting, a transient orchestrator agent collects stakeholder stances, compares the
assumptions underneath them, clears what can be resolved asynchronously, and sends each
participant a compressed brief containing only the items that actually need humans live.

This pitch follows the current Shopee SG 11.11 creator-mix demo. Stop at the generated
pre-meeting brief; do not show a final influencer decision.

## Cold Open

> "Everyone says: we need to reach younger shoppers for 11.11. A summarizer would mark
> that as alignment. But Growth means new users and app installs. Commerce means GMV and
> voucher redemption. The Campaign Lead means mainstream-safe youth reach. Same phrase,
> different assumptions — and that is how a team burns a meeting on fake agreement."

> "Mochi lives in Slack. Before the meeting starts, it DMs the right stakeholders, asks
> what they actually mean, compares the assumptions, clears the easy items, and gives the
> team a two-item agenda instead of a nine-item status walk."

## What's Actually Running

> "The primary entry point is now just a Slack DM. If John writes 'prep the 11.11 mix' and
> includes @mentions with Growth, Commerce, and Lead roles, Mochi parses the roster and
> fans out immediately. If the roster is missing, it asks one setup question. The slash
> command is still there as a hosted fallback."

> "Each stakeholder has a **persistent managed agent session** with structured stance tools:
> position, rationale, assumptions, and confidence. The **orchestrator is transient**. It
> spins up for this Shopee planning meeting, asks Wai Chong, Shang, and John Taylor for
> their stances on each agenda item, runs the assumption-aware classifier, pre-clears the
> action items, DMs the Block Kit digest to the participants, and then dissolves."

> "The important distinction is that we compare assumptions, not just positions. The naive
> baseline sees 'support reaching younger shoppers' and says agreed. The crux finder sees
> acquisition, GMV, and brand reach pulling in different directions."

## Demo Storyboard

| Beat | Time | On Screen | Narration |
|---|---:|---|---|
| 1. Start the prep | 40s | John sends one free-form DM with the Shopee brief and teammate @mentions | "John Taylor starts a pre-meeting for Shopee SG's 11.11 creator campaign without leaving Slack. The decision is not 'who wins' yet; it is how to structure the meeting so the team can decide the creator mix quickly." |
| 2. Fan out to stakeholders | 40s | Mochi parses `<@...> Commerce`, `<@...> Lead`, `me Growth` and opens DMs | "Mochi detects this is a meeting-prep request, maps Slack users to the existing Growth, Commerce, and Lead personas, and asks each person for the exact input needed to compress the agenda." |
| 3. Collect Growth input | 45s | Wai Chong / Growth DM | "Growth wants younger shoppers to mean acquisition: new Shopee users, app installs, first purchases, and CAC after amplification. Mika is the strongest hero candidate from that lens." |
| 4. Collect Commerce input | 45s | Shang / Commerce DM | "Commerce wants 11.11 GMV. Reach matters only if the audience buys, so Shang needs Jayden for Shopee Live conversion, voucher redemption, and live sales discipline." |
| 5. Collect owner input | 40s | John / Lead DM or owner review | "John wants youth relevance without making the national 11.11 campaign too niche or risky. He may split the hero face from the conversion partner." |
| 6. Auto-compile or force compile | 35s | Progress DM; optional `compile` or `/premeeting-compile` | "Mochi tracks who has responded and compiles automatically when all input is in. The owner can force compilation early if the stage clock is tight." |
| 7. Show the 9 to 2 digest | 60s | Slack Block Kit digest in participant DMs, or `scripts/run_demo.py` output | "The final brief compresses nine agenda items down to two: align the primary objective, then decide the creator role mix: one hero partner or hero plus Shopee Live conversion partner." |
| 8. Show the contrast | 35s | Naive baseline or narration | "A position-only baseline says the objective is agreed. The assumption-aware classifier marks it fake agreement because Growth, Commerce, and the owner are using the same words for different success criteria." |
| 9. Codex close | 40s | Tests, code, trace if available | "This is built with OpenAI Agents SDK, Slack Bolt Socket Mode, pydantic contracts, SQLite-backed persistent stances, free-form DM routing, deterministic tests, and a cached fallback for stage timing." |

## The Main Line

> "We are not summarizing the meeting after it happens. We are preventing the wrong
> meeting from happening. The owner still makes the business decision, but the room starts
> with the actual crux instead of rediscovering it live."

## What The Final Brief Should Say

Show this shape, whether it comes from Slack or the offline scripted demo:

```text
Mochi — Prepare Shopee SG 11.11 creator mix decision: hero face, Shopee Live conversion role, and criteria for the split.
Agenda compressed: 9 → 2 items need a meeting

  :large_orange_circle: objective: Everyone says younger shoppers, but success criteria differ.
  [Growth: acquisition and app installs; Commerce: GMV and voucher redemption; Campaign Lead: mainstream-safe youth reach]
  :red_circle: role-mix: The creator role split is unresolved.
  [Wai Chong prefers Mika as hero face; Shang requires Jayden for Shopee Live conversion; John may split hero and conversion roles.]

Action items: 3 resolved, 0 need an owner
Decision owner: John Taylor (owner call with logged dissents)
```

Then name the pre-read items that no longer need live debate:

- short-form video plus Shopee Live
- affiliate links, promo codes, voucher redemption, live GMV, and app-install tracking
- fashion, beauty, and gadgets as hero categories
- paid amplification reserved for install growth
- brand-safety, disclosure, and competitor-sponsorship review
- backup creators if contract or review fails

## Judging Criteria Beats

- **Problem & Solution Fit:** cross-functional campaign planning looks aligned until
  stakeholders define success differently. PMLE finds that before the meeting.
- **Build Quality:** persistent participant agents, transient orchestrator, structured
  pydantic stance contract, SQLite persistence, free-form Slack DM routing, roster
  parsing, participant fan-out, Block Kit digest, deterministic fallback, and offline
  tests.
- **Insight & Originality:** fake-agreement detection is the wedge. The baseline proves
  this is not just summarization.
- **Real-World Value:** fewer live agenda items, less false consensus, action items closed
  before the meeting, and no new tool for the team to adopt.
- **Build Direction:** people send agents into the pre-meeting loop; humans receive only
  unresolved cruxes with provenance.
- **Use of Codex:** Codex helped pivot the scenario, align docs with code, build the
  orchestrator and Slack path, write tests, and harden the demo fallback.

## Why Slack, Why Persistent vs Transient

> "Slack is where the team already is, so the adoption cost is low. Persistent agents are
> useful because each person keeps their working context and stance history across
> meetings. The orchestrator is transient on purpose: it has no standing authority. It
> exists only to prepare this meeting, compress the agenda, and hand control back to the
> human owner."

> "The multi-human flow matters because Mochi is not asking John to impersonate the whole
> room. John can mention the actual stakeholders, Mochi DMs them, tracks responses, and
> sends the compiled brief back to everyone involved."

## What Is Live vs Cached

> "For stage safety, the default Slack path uses offline intent detection and a
> deterministic cached Shopee digest. `/premeeting-scripted` hits the same reliable path.
> That means the final brief is input-independent unless `PMLE_LIVE_AGENTS=1` is set. In
> live mode, the router agent classifies the DM intent, stakeholder replies are grounded
> into persistent stances, and the brief is classified from those stances with real OpenAI
> calls. The script runner has a separate gate: it goes live only when `OPENAI_API_KEY` is
> exported in the shell."

> "The demo claim does not depend on API speed. The claim is that position-only agreement
> misses the real issue, while assumption-aware classification catches it and compresses
> the meeting from nine agenda items to two."

## Judge Q&A

### "Isn't this just a meeting summarizer?"

No. Summarizers act after the meeting. Mochi acts before the meeting and changes what
reaches the room.

### "What is the crux in this demo?"

The surface phrase is "younger shoppers." Growth means acquisition and app installs.
Commerce means sale-window GMV and conversion. The Campaign Lead means youth relevance
without losing mainstream brand safety. The first live agenda item is to decide which
objective governs the creator mix.

### "What is the second live agenda item?"

Whether one creator can cover both roles, or whether the campaign needs a hero face plus a
separate Shopee Live conversion partner. Mika is stronger for youth reach; Jayden is
stronger for live conversion; Nora is safer but less youth-coded; Ari has buzz but higher
brand risk.

### "How do you know the agents aren't making up the stances?"

The structured stances come from stakeholder replies in live mode or from the seeded
Shopee scenario in the deterministic demo path. The contract stores position, rationale,
assumptions, and confidence, and the Slack live path persists those via each participant's
agent.

### "How do you know it isn't staged?"

There are two paths by design. The cached path is deterministic for a reliable stage demo,
including the free-form DM and `/premeeting-scripted` surfaces. The live path is enabled
explicitly with `PMLE_LIVE_AGENTS=1` and real OpenAI calls. The tests lock down that the
default cached path cannot silently leak into the live path.

### "Do agents decide for humans?"

No. The system compresses the agenda and preserves the disagreement. John Taylor remains
the decision owner and can pull any compressed item back into the live meeting.

### "Do agents leak private context?"

The orchestrator operates on structured stances, not raw private history: position,
rationale, assumptions, confidence, and citations to stakeholders.

### "Why OpenAI Agents SDK?"

The demo needs persistent per-person sessions, transient orchestration, function tools for
stance updates, and tracing. The Agents SDK gives those primitives, so the product logic can
focus on assumption comparison.

## Backup Lines

If Slack is slow or flaky:

> "I'll switch to `/premeeting-scripted` or the local demo runner. Same Shopee scenario,
> same nine-to-two digest, no Slack timing dependency."

If a stakeholder has not replied:

> "The owner can DM `compile` or use `/premeeting-compile` to force the brief with the
> input gathered so far."

If live agent grounding is not enabled:

> "This run is using the deterministic cached Shopee stances for stage timing. The live
> path is gated explicitly by `PMLE_LIVE_AGENTS=1` so we do not accidentally confuse a
> reliable demo with a live-input demo."

If the trace is the only thing live:

> "The trace shows the actual orchestrator and participant-agent calls from this run; the
> Slack digest is the product surface."

## Closing

> "Meetings do not fail only because people disagree. They fail because people think they
> agree. Mochi catches that before the hour is gone — right inside Slack."
