from pmle.schemas import AgendaItem, ActionItem

DECISION = "Ship new checkout before the 11.11 promo freeze?"
OWNER = "PM"
PARTICIPANTS = ["PM", "Backend", "SRE", "Security"]

AGENDA = [
    AgendaItem(id="scope",        text="Feature scope finalized"),
    AgendaItem(id="pay-fallback", text="Payment provider fallback"),
    AgendaItem(id="flag-rollout", text="Feature flag rollout"),
    AgendaItem(id="support-comms",text="Customer support comms"),
    AgendaItem(id="analytics",    text="Analytics instrumentation"),
    AgendaItem(id="promo-timing", text="Promo freeze timing"),
    AgendaItem(id="rollback",     text="Rollback owner"),
    AgendaItem(id="load",         text="11.11 load readiness"),
    AgendaItem(id="security",     text="Checkout token/session security posture"),
]

ACTION_ITEMS = [
    ActionItem(id="ai-flag",     text="Confirm feature flag default state"),
    ActionItem(id="ai-rollback", text="Assign a rollback owner for 11.11"),
    ActionItem(id="ai-loadtest", text="Schedule the 11.11 load test"),
]
# Expected: items scope..rollback -> agreed; load -> crux; security -> fake_agreement.
