from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class EligibilityVerdict(str, Enum):
    ELIGIBLE = "eligible"
    BORDERLINE = "borderline"
    NOT_ELIGIBLE = "not_eligible"


class EligibilityReason(BaseModel):
    requirement: str
    student_value: str
    passed: bool
    severity: str = "soft"  # "hard" = disqualifying, "soft" = borderline/preference
    notes: str = ""


class EligibilityResult(BaseModel):
    opportunity_id: str
    verdict: EligibilityVerdict
    score: float = Field(ge=0, le=1)
    reasons: list[EligibilityReason] = Field(default_factory=list)
    summary: str = ""
    narration: list[str] = Field(default_factory=list)


class EligibilityBatchResult(BaseModel):
    results: list[EligibilityResult]
    eligible_count: int = 0
    borderline_count: int = 0
    rejected_count: int = 0
    narration: list[str] = Field(default_factory=list)