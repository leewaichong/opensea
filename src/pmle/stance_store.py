import json
import sqlite3
from typing import Optional
from pmle.schemas import Stance


class StanceStore:
    """SQLite-backed structured Stance contract, keyed by (person, item_id). Persistent."""

    def __init__(self, db_path: str = "pmle_stances.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS stances "
            "(person TEXT, item_id TEXT, payload TEXT, PRIMARY KEY (person, item_id))"
        )
        self.conn.commit()

    def set(self, person: str, stance: Stance) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO stances VALUES (?, ?, ?)",
            (person, stance.item_id, stance.model_dump_json()),
        )
        self.conn.commit()

    def get(self, person: str, item_id: str) -> Optional[Stance]:
        row = self.conn.execute(
            "SELECT payload FROM stances WHERE person=? AND item_id=?", (person, item_id)
        ).fetchone()
        return Stance.model_validate_json(row[0]) if row else None

    def update(self, person: str, item_id: str, partial: dict) -> Stance:
        current = self.get(person, item_id)
        base = current.model_dump() if current else {"stakeholder": person, "item_id": item_id,
                                                     "position": "neutral", "rationale": ""}
        base.update(partial)
        merged = Stance.model_validate(base)
        self.set(person, merged)
        return merged

    def all_for_item(self, item_id: str) -> list[Stance]:
        rows = self.conn.execute(
            "SELECT payload FROM stances WHERE item_id=?", (item_id,)
        ).fetchall()
        return [Stance.model_validate_json(r[0]) for r in rows]
