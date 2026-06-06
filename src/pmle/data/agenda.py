from pmle.schemas import AgendaItem, ActionItem

DECISION = "Prepare Shopee SG 11.11 creator mix decision: hero face, Shopee Live conversion role, and criteria for the split."
OWNER = "John Taylor"
PARTICIPANTS = ["Wai Chong", "Shang", "John Taylor"]

AGENDA = [
    AgendaItem(id="objective",     text="Align on the primary campaign objective"),
    AgendaItem(id="role-mix",      text="Decide creator role mix: hero face vs Shopee Live conversion partner"),
    AgendaItem(id="creator-owner", text="Choose which creator should own each role"),
    AgendaItem(id="deliverables",  text="Confirm deliverables: short-form videos, livestream slots, affiliate content"),
    AgendaItem(id="tracking",      text="Confirm tracking: affiliate links, promo codes, voucher redemption, app installs"),
    AgendaItem(id="brand-safety",  text="Review brand-safety and competitor-sponsorship risks"),
    AgendaItem(id="categories",    text="Confirm hero product categories"),
    AgendaItem(id="budget",        text="Confirm budget split between creator fees and paid amplification"),
    AgendaItem(id="backups",       text="Identify backup creators if contract or review fails"),
]

ACTION_ITEMS = [
    ActionItem(id="ai-live-slot", text="Confirm at least one Shopee Live slot is required"),
    ActionItem(id="ai-tracking",  text="Confirm affiliate links, promo codes, voucher redemption, live GMV, and app-install tracking"),
    ActionItem(id="ai-safety",    text="Confirm brand-safety, disclosure, and competitor-sponsorship review before contracting"),
]
# Expected: 9 starting agenda items compress to objective + role-mix.
