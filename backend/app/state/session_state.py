from typing import TypedDict, Annotated
from operator import add
from app.models.profile import StudentProfile, ProfileExtractionResult
from app.models.opportunity import Opportunity, DiscoveryResult
from app.models.eligibility import EligibilityResult, EligibilityBatchResult
from app.models.match import MatchResult
from app.models.application import ApplicationResult
from app.models.tracker import TrackerResult
from typing import Optional


class SessionState(TypedDict, total=False):
    session_id: str
    phase: str
    raw_resume_text: str
    profile_result: Optional[ProfileExtractionResult]
    profile: Optional[StudentProfile]
    discovery_result: Optional[DiscoveryResult]
    opportunities: list[Opportunity]
    eligibility_result: Optional[EligibilityBatchResult]
    eligibility_results: list[EligibilityResult]
    match_result: Optional[MatchResult]
    application_results: Annotated[list[ApplicationResult], add]
    tracker_result: Optional[TrackerResult]
    narration: Annotated[list[str], add]
    errors: Annotated[list[str], add]