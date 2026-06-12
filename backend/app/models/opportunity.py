from enum import Enum
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class OpportunityType(str, Enum):
    SCHOLARSHIP = "scholarship"
    INTERNSHIP = "internship"


class Opportunity(BaseModel):
    id: str
    title: str
    type: OpportunityType
    organization: str
    amount: Optional[str] = None
    deadline: Optional[date] = None
    url: Optional[str] = None
    location: Optional[str] = None
    duration: Optional[str] = None
    description: str
    requirements: list[str] = Field(default_factory=list)
    citizenship_requirements: list[str] = Field(default_factory=list)
    gpa_requirement: Optional[float] = None
    degree_levels: list[str] = Field(default_factory=list)
    fields_of_study: list[str] = Field(default_factory=list)
    skills_required: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source: str = "knowledge_base"


class DiscoveryResult(BaseModel):
    opportunities: list[Opportunity]
    total_found: int
    search_queries_used: list[str] = Field(default_factory=list)
    narration: list[str] = Field(default_factory=list)