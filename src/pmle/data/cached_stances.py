from pmle.schemas import Stance

# Minimal but sufficient: the security item shows the fake-agreement trap; load shows a real crux.
CACHED: list[Stance] = [
    # security — same word "secure", conflicting assumptions
    Stance(stakeholder="PM", item_id="security", position="support",
           rationale="Secure via server-side session is fine.",
           key_assumptions=["Server-side session"], confidence=0.8),
    Stance(stakeholder="Backend", item_id="security", position="support",
           rationale="Server controls the session; we're good.",
           key_assumptions=["Server-side session"], confidence=0.8),
    Stance(stakeholder="Security", item_id="security", position="agree_with_condition",
           rationale="Only if NO checkout token is stored client-side.",
           key_assumptions=["No client-side token storage"], confidence=0.9),
    # load — real crux
    Stance(stakeholder="SRE", item_id="load", position="block",
           rationale="Checkout has not passed 11.11 traffic simulation.",
           key_assumptions=["Traffic may exceed last peak by 35%"], confidence=0.85),
    Stance(stakeholder="PM", item_id="load", position="support",
           rationale="We can throttle promos if needed.", key_assumptions=[], confidence=0.6),
]
