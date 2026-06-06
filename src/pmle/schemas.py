from typing import Literal, Optional
from pydantic import BaseModel, Field

Position = Literal["support", "agree_with_condition", "neutral", "block"]
ItemStatus = Literal["open", "agreed", "fake_agreement", "crux", "needs_clarification"]
ActionStatus = Literal["open", "resolved", "reassigned", "needs_owner"]


class Stance(BaseModel):
    stakeholder: str
    item_id: str
    position: Position
    rationale: str
    key_assumptions: list[str] = Field(default_factory=list)
    confidence: float = 0.5
    evidence_refs: list[str] = Field(default_factory=list)


class AgendaItem(BaseModel):
    id: str
    text: str


class ActionItem(BaseModel):
    id: str
    text: str
    status: ActionStatus = "open"
    resolution: Optional[str] = None
    owner: Optional[str] = None
    resolved_by: list[str] = Field(default_factory=list)


class ClassificationResult(BaseModel):
    item_id: str
    status: ItemStatus
    summary: str
    divergence: Optional[str] = None
    cited_stances: list[str] = Field(default_factory=list)
    follow_up: Optional[str] = None


class BoardState(BaseModel):
    decision: str
    owner: str
    items: list[ClassificationResult] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)

    def meeting_item_count(self) -> int:
        return sum(1 for i in self.items if i.status in ("crux", "fake_agreement"))
