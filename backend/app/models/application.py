from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class DocumentType(str, Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    SOP = "sop"


class GeneratedDocument(BaseModel):
    type: DocumentType
    opportunity_id: str
    content: str
    tailored: bool = True


class ApplicationResult(BaseModel):
    opportunity_id: str
    opportunity_title: str
    documents: list[GeneratedDocument] = Field(default_factory=list)
    narration: list[str] = Field(default_factory=list)