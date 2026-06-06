from pmle.schemas import Stance

# Shopee SG 11.11 creator mix scenario. Minimal but sufficient: the objective
# item shows fake agreement around "younger shoppers"; role-mix is a real crux.
CACHED: list[Stance] = [
    Stance(stakeholder="Wai Chong", item_id="objective", position="support",
           rationale="Target younger shoppers, meaning new Shopee app users and first purchases.",
           key_assumptions=["Younger shoppers means acquisition", "Success is new users, app installs, first purchases, and CAC"], confidence=0.9),
    Stance(stakeholder="Shang", item_id="objective", position="support",
           rationale="Target younger shoppers only if they actually buy during 11.11.",
           key_assumptions=["Younger shoppers means GMV, conversion, voucher redemption, and live sales"], confidence=0.9),
    Stance(stakeholder="John Taylor", item_id="objective", position="agree_with_condition",
           rationale="The campaign should feel youth-relevant while staying mainstream-safe.",
           key_assumptions=["Younger shoppers means mainstream youth reach without brand-safety risk"], confidence=0.85),
    Stance(stakeholder="Wai Chong", item_id="role-mix", position="support",
           rationale="Mika Tan should be the hero face for TikTok-native youth acquisition.",
           key_assumptions=["Hero face should optimize acquisition", "Mika is strongest for 18-24 reach"], confidence=0.86),
    Stance(stakeholder="Shang", item_id="role-mix", position="block",
           rationale="Do not choose one viral hero without a strong Shopee Live conversion engine.",
           key_assumptions=["Jayden Cho should own Shopee Live conversion", "Conversion is not a secondary detail"], confidence=0.9),
    Stance(stakeholder="John Taylor", item_id="role-mix", position="agree_with_condition",
           rationale="Use a mainstream-safe hero face, potentially with a separate conversion partner.",
           key_assumptions=["Hero face can be Mika or Nora", "Jayden may be conversion partner rather than hero"], confidence=0.82),
]
