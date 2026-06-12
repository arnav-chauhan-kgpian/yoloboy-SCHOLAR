import pytest
from app.models.application import GeneratedDocument, DocumentType, ApplicationResult


class TestApplicationModels:
    def test_document_types(self):
        assert DocumentType.RESUME.value == "resume"
        assert DocumentType.COVER_LETTER.value == "cover_letter"
        assert DocumentType.SOP.value == "sop"

    def test_application_result(self):
        doc = GeneratedDocument(
            type=DocumentType.RESUME,
            opportunity_id="opp1",
            content="My tailored resume content",
        )
        result = ApplicationResult(
            opportunity_id="opp1",
            opportunity_title="Test Opp",
            documents=[doc],
        )
        assert len(result.documents) == 1
        assert result.documents[0].type == DocumentType.RESUME