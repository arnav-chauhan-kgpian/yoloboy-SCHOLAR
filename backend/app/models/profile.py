from enum import Enum
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class CitizenshipStatus(str, Enum):
    US_CITIZEN = "us_citizen"
    PERMANENT_RESIDENT = "permanent_resident"
    INTERNATIONAL = "international"
    DACA = "daca"


class EnrollmentStatus(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"


class StudentProfile(BaseModel):
    name: str
    email: str
    citizenship: CitizenshipStatus
    enrollment: EnrollmentStatus
    gpa: Optional[float] = None
    major: str
    university: str
    degree_level: str
    graduation_date: Optional[date] = None
    skills: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    extracurriculars: list[str] = Field(default_factory=list)
    financial_need: Optional[str] = None
    location_preferences: list[str] = Field(default_factory=list)
    raw_resume_text: Optional[str] = None


class ProfileExtractionResult(BaseModel):
    profile: StudentProfile
    confidence: float = Field(ge=0, le=1)
    missing_fields: list[str] = Field(default_factory=list)
    narration: list[str] = Field(default_factory=list)