# AGENTS.md — PerMyLastEmail (PMLE)

## Overview

PerMyLastEmail (PMLE) is a Slack-native pre-meeting **crux finder**. You DM the bot in plain
language ("prep the Q3 vendor decision — @alice owns budget, @bob runs eng"); it deduces that
you want to prepare a meeting, reaches out to the **real teammates** you tagged, collects each
person's input, compares the *assumptions* underneath their stances (not just their surface
positions), and DMs everyone a compressed brief: which items are genuine conflicts that need
the live meeting, which only one side weighed in on, and which are already aligned. The point
is to catch **fake agreement** — people using the same words to mean different things — before
anyone sits down. Built for the Sea x OpenAI Codex Hackathon (team PerMyLastEmail).

**Tech:** Python 3.11+, OpenAI Agents SDK (`openai-agents` → `import agents`),
`slack-bolt` Socket Mode, pydantic v2, SQLite, pytest.

## Entry point & flow

There is **no slash command to start** — the entry point is a free-form DM. `on_dm` in
`slack_app.py` routes every DM:

```
DM ──> "clear"/"reset"/"restart"? ──> wipe state, reset scenario (kill switch)
   ──> already in a setup session / meeting? ──> continue it
   ──> fresh DM:
         @mentioned real teammates?  ──> MULTI-PARTICIPANT: DM each for input,
                                          collect, auto-compile, DM the brief to all
         prep intent but no mentions? ──> ask the one setup question, then fan out
         not a meeting?               ──> the persistent agent just replies
```

The compiled brief is **DM'd to every participant** (and the initiator) — there is no meeting
channel. Auto-compiles once everyone replies, or the initiator DMs `compile`.

## Two gates (the most important non-obvious behavior)

Behavior is controlled by two env vars, read in `slack_app.py`:

| | `PMLE_LIVE_AGENTS` unset/`0` | `PMLE_LIVE_AGENTS=1` |
|---|---|---|
| **`PMLE_HARDCODED=1`** | deterministic cached **Shopee** digest (offline, no key, input-independent — safe for stage timing) | live LLM, but the **fixed Shopee scenario**: 9-item agenda, 3 personas, grounding pinned to `objective`/`role-mix`, hardcoded action items |
| **`PMLE_HARDCODED` unset/`0`** | (same as left — demo can't be dynamic without the LLM) | **FULL DYNAMIC** flow ↓ |

`_dynamic() = _live_agents() and PMLE_HARDCODED != "1"`. **Dynamic only applies to the
multi-participant branch** (you @mention real people); the solo branch is always canned Shopee.

**Dynamic live flow:** the agenda is generated from your setup (`triage.build_agenda`), roles
are free-text lenses inferred from the text (`triage.llm_roster(open_roles=True)`), each real
reply is grounded into stances over the *real* agenda (`triage.ground_reply`, filtered to the
exact agenda ids, keyed by **slack id** so same-role people don't clobber), and **Mochi**
(`crux_engine`) classifies. No personas, no hardcoded topic — `_build_dynamic_board(meeting)`.

## Modules (`src/pmle/`)

- **`schemas.py`** — the **locked shared data contract** (pydantic v2): `Stance` (position,
  rationale, `key_assumptions`, confidence), `AgendaItem`, `ActionItem`, `ClassificationResult`
  (status ∈ `agreed`/`fake_agreement`/`crux`/`needs_clarification`/`open`), `BoardState`.
  Everything keys off it.
- **`slack_app.py`** — Socket Mode entrypoint (`main()`). `on_dm` routing, `_dynamic()` gate,
  `_extract_roster`, `_start_multihuman` (DM resilience + dynamic agenda build), `_handle_meeting_dm`,
  `_ground_meeting_reply`, `_build_dynamic_board`, `_compile_and_post`, the `/clear` kill switch
  (`_full_reset`), and the hardcoded helpers (`_build_board`, `_ground_stance`).
- **`triage.py`** — the LLM "deduce structure from NL" layer: `heuristic_intent`/`llm_intent`
  (is this a meeting request?), `llm_roster(open_roles)` (tagged user → role), `build_agenda`
  (setup → {decision, owner, agenda}), `ground_reply` (reply → stances over the agenda).
- **`meeting.py`** — Slack-free core for the multi-participant flow: `parse_participants` and
  `extract_targets` (parse the roster from the setup), `ROLE_TO_PERSONA`, and the `Meeting`
  dataclass (participants, responses, phase, + dynamic `decision`/`owner`/`agenda`/`stances`).
- **`crux_engine.py`** — `classify_item(stances)` is the assumption-aware classifier (the
  **Mochi** agent). `naive_baseline` is the position-only foil that deliberately misses fake
  agreement (eval contrast).
- **`orchestrator.py`** — `run_meeting(...)` for the **hardcoded** path: loops the fixed agenda,
  asks each persona, classifies, pre-clears Shopee action items. `ask_stance=`/`classify_item=`
  are injectable (demo path) and fall back to module globals (test monkeypatching).
- **`participants.py`** — `build_participant(person)` → persona `Agent` + persistent
  `SQLiteSession("participant::<person>", "pmle_sessions.db")`. Used by the hardcoded/solo path.
- **`stance_store.py`** — `StanceStore` (SQLite `pmle_stances.db`, keyed by `(person, item_id)`).
- **`manual_flow.py`** — pure state machine for the **solo** setup flow (`brief → setup →
  growth → commerce → owner_gap → confirm_* → complete`).
- **`digest.py`** — renders `BoardState` to text/Block Kit. Four distinct buckets kept
  consistent with the header count: `_DISCUSS` (crux+fake = "needs the meeting", the headline
  count), `_CLARIFY` (needs_clarification = "needs more input"), `_NO_INPUT` (open), `_RESOLVED`
  (agreed). Footer derives from the same buckets so header/sections/footer can't disagree.
- **`data/`** — `agenda.py` (Shopee decision, 9 agenda items, 3 action items), `cached_stances.py`
  (`CACHED` seeded Shopee stances), `personas.py` (private persona context — hardcoded path only).

## Slack surface

- **Entry:** free-form DM (primary). Type `clear`/`reset`/`restart` to reset at any point.
- **Slash commands:** `/premeeting` (manual fallback that opens the setup flow), `/premeeting-compile`
  (force-compile a pending meeting), `/premeeting-scripted` (fast cached digest), `/clear`
  (kill switch — needs registering in the Slack app config; typed `clear` works without it).
- **Manifest** (per the `slack_app.py` header): Socket Mode ON; bot scopes `chat:write`,
  `im:write`, `im:history`, `commands`, `app_mentions:read`; subscribe to `message.im`.

## Commands

```bash
pip install -e ".[dev]"            # editable install with pytest extras

python -m pytest -q                # 58 tests, ~1s, fully offline (LLM stubbed/injected)
python scripts/run_demo.py         # offline 9→2 hardcoded digest to stdout (deterministic)
python scripts/seed_sessions.py    # load CACHED stances into pmle_stances.db
python -c "import pmle.slack_app; print('ok')"   # import smoke

# Start the Socket Mode app (needs SLACK_BOT_TOKEN + SLACK_APP_TOKEN):
python -m pmle.slack_app                              # default: demo/canned, offline
PMLE_LIVE_AGENTS=1 python -m pmle.slack_app           # live + DYNAMIC (real OpenAI calls)
PMLE_LIVE_AGENTS=1 PMLE_HARDCODED=1 python -m pmle.slack_app   # live but canned Shopee
```

Clean restart for a live demo: `pkill -f pmle.slack_app; rm -f pmle_sessions.db*;
python scripts/seed_sessions.py; PMLE_LIVE_AGENTS=1 python -m pmle.slack_app`.

## Environment variables

`OPENAI_API_KEY` (live only), `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN` (start the server),
`PMLE_HUMAN_USER` (scripted-escalation target). `PMLE_LIVE_AGENTS` and `PMLE_HARDCODED` are the
gates above — referenced only in code, set them explicitly. (`PMLE_MEETING_CHANNEL` is gone —
the brief is DM'd to participants, there is no channel.)

## Conventions & gotchas

- **`schemas.py` is the locked contract** — change deliberately; stored JSON depends on it.
- **Tests are offline & deterministic** — they stub/inject the LLM (no network, no key). 58
  tests. Live tests pin `PMLE_HARDCODED=1` so the default-dynamic flip doesn't call real agents;
  new dynamic tests mock `build_agenda`/`ground_reply`/`llm_roster`/`classify_item`.
- **Generated local artifacts must NOT be committed:** `pmle_sessions.db*`, `pmle_stances.db`,
  `src/pmle.egg-info/`, `tasks/` (covered by `.git/info/exclude`).
- **State is in-memory** — `_PENDING_MEETINGS`/`_USER_TO_MEETING`/per-meeting `stances` live in
  the process. Restarting drops in-flight meetings. `clear` resets per-user; a host restart is
  the cold reset.
- **In-band mode tells** (for debugging what produced a brief): the hardcoded path is always
  exactly `9 → 2` with `N action items cleared`; the dynamic path varies and shows `N for the
  meeting · N need more input · N already aligned` with no action-item line.
- **Don't start a second Socket Mode server** if one is running; never commit/print secrets
  (`.env` is gitignored).
