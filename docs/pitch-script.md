---
date: 2026-06-06
tags: [project, hackathon, pitch]
status: active-plan
---

# Pitch Script - 3-Minute Demo

## Cold Open

> "Four people said: make checkout secure. A summarizer would mark that as agreement. But PM and Backend meant server-side sessions, while Security meant no client-side token at all. Same words, different assumptions. That is how a team accidentally ships the wrong design into 11.11."

> "We built PerMyLastEmail: a pre-meeting crux finder. It uses managed agents to collect stakeholder stances before the meeting, compares the assumptions underneath those stances, and gives humans only the fights that matter."

## Demo Storyboard

| Beat | Time | On Screen | Narration |
|---|---:|---|---|
| 1. Setup | 20s | Decision room: "Ship new checkout before 11.11 freeze?" | "This is a typical go/no-go meeting: 4 stakeholders, 9 agenda items, high launch pressure." |
| 2. Run agents | 25s | PM, Backend, SRE, Security agents generating stances | "Each stakeholder agent receives the public brief plus its private context and emits structured stances: position, rationale, assumptions, confidence, and evidence." |
| 3. Board resolves | 35s | 7 items turn green, counter drops | "Seven items were genuine agreement. Those should not consume meeting time." |
| 4. Obvious crux | 20s | Load-readiness item stays red | "One item is a real disagreement: SRE is not comfortable with 11.11 traffic readiness." |
| 5. Fake agreement | 45s | Security item turns amber, assumption diff opens | "This is the important one. Everyone said 'secure checkout,' so the naive baseline says agreed. But assumption-aware classification catches the mismatch: PM and Backend assume server-side session; Security means no client-side token. This becomes the second real meeting item." |
| 6. Decision record | 25s | Final agenda: 2 items, evidence and dissents | "The meeting is now 2 items, not 9. The human owner still decides, with provenance, evidence, and dissents preserved." |
| 7. Codex/OpenAI close | 30s | Eval tests passing, build trail | "We used OpenAI agents for the stakeholder simulation and Codex to build and red-team the classifier. The key engineering choice was cutting live infrastructure and spending the day proving the reasoning layer." |

## The Main Line

Use this exact phrase:

> "The product is not summarizing the meeting after it happens. It is preventing the wrong meeting from happening in the first place."

## What To Say About Managed Agents

> "We use managed agents as the stakeholder layer. Each agent has a role, private context, and a structured output contract. That lets us spend our hackathon time on the product logic: comparing assumptions and extracting cruxes."

## What To Say About What Is Live

> "For demo reliability, stakeholder responses can be cached. The assumption-diff classification runs on those structured stances, and we keep deterministic fallback output so stage timing does not decide the demo."

If asked whether this is fair:

> "Yes. The core claim is not that the API call is slow or fast. The claim is that position-only classification misses fake agreement, while assumption-aware classification catches it. That is what we show with the baseline and evals."

## Judge Q&A

### "Isn't this just a meeting summarizer?"

No. Summarizers act after the meeting. This acts before the meeting and catches hidden disagreement that a transcript summary would often flatten.

### "How do you know it is not staged?"

We show three things:

1. the naive baseline fails on the security item,
2. the assumption diff explains exactly why,
3. the eval suite includes a false-positive trap where different wording has the same assumption and should still classify as agreed.

### "Do agents decide for humans?"

No. The system compresses the agenda. The human owner still makes the decision. Every compressed item has provenance and can be pulled back into the meeting.

### "Do agents leak private context?"

No raw private context is shared. Agents emit structured stances: position, rationale, assumptions, confidence, and evidence references.

### "Why not build live agent joining?"

Because live joining is infrastructure proof, not product proof. For a one-day hackathon, the valuable proof is catching the hidden disagreement that changes the decision.

### "Why OpenAI?"

The project needs structured multi-agent reasoning. OpenAI gives us reliable structured outputs and agent workflows; Codex helped us simplify the architecture and build the classifier, UI, and tests quickly.

## Backup Lines

If the demo is slow:

> "We will switch to cached stances so we can focus on the reasoning result."

If the classifier output is delayed:

> "The deterministic fallback shows the same board state from the last successful run."

If the judges push on scope:

> "We intentionally scoped this to the crux-finding layer. That is the part with product novelty."

## Closing

> "Meetings do not fail because people disagree. They fail because people think they agree. PerMyLastEmail catches that before the hour is gone."
