# AGENTS.md — PerMyLastEmail (PMLE)

## Overview

PerMyLastEmail (PMLE) is a Slack-native pre-meeting **crux finder**. A transient
orchestrator agent queries persistent per-person managed agents, compares the
*assumptions* underneath their stances (not just their surface positions), classifies
each agenda item (`agreed` / `fake_agreement` / `crux` / `needs_clarification`),
pre-clears resolvable action items, and posts a compressed "9 → 2" digest to Slack — only
the items that actually need a live meeting reach humans. Built for the Sea x OpenAI Codex
Hackathon.

**Tech:** Python 3.11+, OpenAI Agents SDK (`openai-agents` → `import agents`),
`slack-bolt` Socket Mode, pydantic v2, SQLite, pytest.

## Architecture & Data Flow

```
human (Slack DM) ──> persistent participant Agent (SQLiteSession per person)
                          │  owns structured Stance via set/update_stance tools
                          ▼
                     StanceStore (SQLite: pmle_stances.db, keyed by person+item_id)
                          ▲
   orchestrator.run_meeting() (transient, per-meeting) reads stances ──┘
                          │
                          ▼
   crux_engine.classify_item (assumption-aware LLM)  OR  naive_baseline (position-only)
                          ▼
                     BoardState ──> digest.render_text / render_blocks ──> Slack
```

- **`src/pmle/schemas.py`** — the **locked shared data contract** (pydantic v2). `Stance`
  (position, rationale, `key_assumptions`, confidence), `AgendaItem`, `ActionItem`,
  `ClassificationResult`, `BoardState`. Change deliberately — everything keys off it.
- **`participants.py`** — `build_participant(person)` returns an `Agent` + persistent
  `SQLiteSession("participant::<person>", "pmle_sessions.db")` with `get/set/update_stance`
  function-tools. `ask_stance()` is what the orchestrator calls per (person, item); it
  short-circuits to the cached `StanceStore` value if one exists.
- **`stance_store.py`** — `StanceStore`, SQLite-backed, keyed by `(person, item_id)`.
  Persistent across meetings.
- **`crux_engine.py`** — `classify_item(stances)` is the assumption-aware LLM classifier
  (the `_CLASSIFIER` Agent). `naive_baseline(stances)` is the deterministic position-only
  foil that *deliberately misses* fake agreement (used in evals to show the contrast).
- **`orchestrator.py`** — `run_meeting(escalate=None, ask_stance=None, classify_item=None)`.
  Loops agenda items, asks each participant, classifies, optionally escalates
  `needs_clarification` to a human via the `escalate` hook, then deterministically
  pre-clears the Shopee action items. The `ask_stance=`/`classify_item=` params let a
  caller **inject** the stance source/classifier (Slack demo path); when `None` they fall
  back to the module-level functions, so test monkeypatching of `orchestrator.ask_stance`
  still works.
- **`digest.py`** — renders `BoardState` to plain text (`render_text`) and Slack Block Kit
  (`render_blocks`). Only `crux`/`fake_agreement` items show in the "needs a meeting" list.
- **`manual_flow.py`** — pure, I/O-free conversation **state machine** for the `/premeeting`
  DM flow (`brief → setup → growth → commerce → owner_gap → confirm_growth →
  confirm_commerce → complete`). Returns `{reply, ground, complete}` signals; the Slack
  layer applies the side effects.
- **`slack_app.py`** — `slack-bolt` Socket Mode entrypoint (`main()` starts the server).
- **`data/`** — `agenda.py` (decision, 9 agenda items, 3 action items, participants),
  `cached_stances.py` (`CACHED` — the seeded Shopee stances), `personas.py` (private agent
  context per person).

## Slack Commands & the Key Gate (most important non-obvious behavior)

Two slash commands (defined in `slack_app.py`):

- **`/premeeting`** — opens a DM and hosts the dynamic flow driven by `manual_flow.py`.
  Each stakeholder reply is grounded into a participant's `Stance`; the brief is generated
  from collected inputs.
- **`/premeeting-scripted`** — the fast, deterministic cached fallback (canned Shopee
  digest). Safe for stage/demo timing.

**Brief generation is gated by the `PMLE_LIVE_AGENTS` env var** (read only in
`slack_app.py._live_agents()`):

| `PMLE_LIVE_AGENTS` | Behavior |
|---|---|
| unset / `0` (default) | Deterministic **cached Shopee digest**, input-independent. `run_meeting` is called with `ask_stance=_demo_ask_stance, classify_item=_demo_classify_item`. Safe for demo timing. |
| `1` | Grounds the user's typed inputs into stances via persistent agents, then classifies **live**. Only mode where the brief reflects what the user typed. Needs `OPENAI_API_KEY`; non-deterministic; slow (the code header says "~21 extra agent calls"). |

> **Two different live gates — don't conflate them.** `slack_app.py` gates on
> `PMLE_LIVE_AGENTS == "1"`. `scripts/run_demo.py` instead gates on **`OPENAI_API_KEY`
> presence** and does *not* call `load_dotenv()`, so a key in `.env` will **not** trigger
> the live path there — only a shell-exported key does. Likewise the injection style
> differs: `slack_app` injects via the `ask_stance=`/`classify_item=` params, while
> `run_demo` still **monkeypatches** `orchestrator.ask_stance`/`classify_item` globals
> (the orchestrator supports both deliberately).

## Commands (all fast & offline except the live path)

```bash
pip install -e ".[dev]"            # editable install with pytest extras

python -m pytest -q                # 17 tests, ~1s, fully offline (LLM calls stubbed)
python -m pytest -v                # verbose

python scripts/run_demo.py         # offline 9→2 digest to stdout (deterministic)
python scripts/seed_sessions.py    # load CACHED stances into pmle_stances.db
python -c "import pmle.slack_app; print('ok')"   # import smoke

# LIVE — slow/costly, makes real OpenAI calls; do NOT run casually:
OPENAI_API_KEY=sk-... python scripts/run_demo.py      # run_demo live path
# (Slack app live path: set PMLE_LIVE_AGENTS=1 and drive /premeeting)

python -m pmle.slack_app           # starts Socket Mode server (needs Slack tokens)
```

### Verified output (run during doc authoring)

- `python -m pytest -q` → `17 passed in 0.89s`
- `python scripts/run_demo.py` →
  ```
  PerMyLastEmail — Prepare Shopee SG 11.11 creator mix decision: ...
  Agenda compressed: 9 → 2 items need a meeting
    :large_orange_circle: objective: Everyone says younger shoppers, but success criteria differ. [...]
    :red_circle: role-mix: The creator role split is unresolved. [...]
  Action items: 3 resolved, 0 need an owner
  Decision owner: John Taylor (owner call with logged dissents)
  ```
- `python -c "import pmle.slack_app; print('ok')"` → `ok`

## Environment Variables

From `.env.example` (5 vars): `OPENAI_API_KEY`, `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`,
`PMLE_MEETING_CHANNEL`, `PMLE_HUMAN_USER`.

> `PMLE_LIVE_AGENTS` is **NOT** in `.env.example` — it is referenced only in code
> (`slack_app.py`). It is the key gate above; set it explicitly when you want the live path.

**Slack manifest** (per the header comment in `slack_app.py`): Socket Mode ON; bot scopes
`chat:write`, `im:write`, `im:history`, `commands`, `app_mentions:read`; slash commands
`/premeeting` and `/premeeting-scripted`; subscribe to `message.im`.

## Conventions & Gotchas

- **`schemas.py` is the locked contract.** All modules, tests, and stored JSON depend on
  it; change it deliberately and update the SQLite payloads accordingly.
- **Tests are offline & deterministic** — they stub/inject the LLM (no network, no key
  needed). 17 tests across `test_crux_engine`, `test_manual_flow`, `test_orchestrator`,
  `test_schemas`, `test_slack_brief`, `test_stance_store`. `test_slack_brief.py` is the one
  that locks down which brief path each mode takes (prevents the canned path leaking into
  the live path).
- **Generated local artifacts must NOT be committed:** `pmle_sessions.db*`,
  `pmle_stances.db`, `src/pmle.egg-info/`. (`.gitignore` covers `.env`, `__pycache__/`,
  `.pytest_cache/`, build dirs — but it does **not** currently list the `*.db` files, so be
  careful not to `git add` them.)
- **The live path mutates `pmle_stances.db`.** After any live run, re-run
  `python scripts/seed_sessions.py` to reset the cached Shopee stances.
- **`import smoke` works without real tokens** because `slack_app.py` constructs the Bolt
  `App` with `token_verification_enabled=False` and a placeholder token; `main()` still
  requires real `SLACK_BOT_TOKEN`/`SLACK_APP_TOKEN` to start.
- **Legacy "checkout / Security" scenario drift.** `README.md`, `docs/design-spec-slack.md`,
  the `orchestrator.py` `escalate("Security", ...)` call, and the `.env.example` comment on
  `PMLE_HUMAN_USER` ("Security stakeholder") are leftovers from an earlier secure-checkout
  scenario. The **live code implements the Shopee SG 11.11 creator-mix** scenario
  (participants: Wai Chong / Growth, Shang / Commerce, John Taylor / Campaign Lead+owner).
  The escalation path is also **not exercised** by the demo — no cached item classifies as
  `needs_clarification`. Trust the code/data over the prose.
- **Docs** live in `docs/`: `build-plan-slack.md`, `design-spec-slack.md`,
  `demo-scenario-shopee.md`, `pitch-script.md`.
- **Do not start a second Socket Mode server** if one is already running, and never commit
  or print secret values (`.env` is gitignored).
