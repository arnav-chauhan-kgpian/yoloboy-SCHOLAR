from pydantic import BaseModel, Field
from typing import Optional, ClassVar


class RankedOpportunity(BaseModel):
    opportunity_id: str
    title: str
    organization: str
    type: str
    match_score: float = Field(ge=0, le=1)
    eligibility_score: float = Field(ge=0, le=1)
    academic_fit: float = Field(ge=0, le=1)
    goals_fit: float = Field(ge=0, le=1)
    skills_fit: float = Field(ge=0, le=1)
    urgency: float = Field(ge=0, le=1)
    eligibility_verdict: str
    deadline: Optional[str] = None


class MatchResult(BaseModel):
    ranked_opportunities: list[RankedOpportunity]
    top_picks: list[RankedOpportunity] = Field(default_factory=list)
    narration: list[str] = Field(default_factory=list)