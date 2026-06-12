from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class TrackerEntry(BaseModel):
    opportunity_id: str
    title: str
    deadline: Optional[date] = None
    status: str = "pending"
    days_remaining: Optional[int] = None
    priority: str = "medium"


class ActionPlan(BaseModel):
    immediate: list[TrackerEntry] = Field(default_factory=list)
    upcoming: list[TrackerEntry] = Field(default_factory=list)
    watchlist: list[TrackerEntry] = Field(default_factory=list)


class TrackerResult(BaseModel):
    action_plan: ActionPlan
    narration: list[str] = Field(default_factory=list)