from pmle.schemas import Stance
from pmle.stance_store import StanceStore


def test_set_get_update(tmp_path):
    store = StanceStore(db_path=str(tmp_path / "s.db"))
    s = Stance(stakeholder="Security", item_id="sec", position="support",
               rationale="ok", key_assumptions=["a"], confidence=0.7)
    store.set("Security", s)
    assert store.get("Security", "sec").position == "support"

    store.update("Security", "sec", {"position": "agree_with_condition",
                                     "key_assumptions": ["no client token"]})
    got = store.get("Security", "sec")
    assert got.position == "agree_with_condition"
    assert got.key_assumptions == ["no client token"]


def test_persists_across_instances(tmp_path):
    db = str(tmp_path / "s.db")
    s = Stance(stakeholder="PM", item_id="x", position="support", rationale="r")
    StanceStore(db_path=db).set("PM", s)
    assert StanceStore(db_path=db).get("PM", "x").stakeholder == "PM"  # survives reopen
