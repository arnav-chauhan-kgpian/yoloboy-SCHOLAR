import pytest
import json
from app.models.profile import (
    StudentProfile, ProfileExtractionResult, CitizenshipStatus, EnrollmentStatus
)
from app.agents.profile_agent import ProfileAgent


class TestProfileModels:
    def test_student_profile_defaults(self):
        p = StudentProfile(
            name="Test Student",
            email="test@example.com",
            citizenship=CitizenshipStatus.INTERNATIONAL,
            enrollment=EnrollmentStatus.FULL_TIME,
            major="CS",
            university="Test U",
            degree_level="Bachelor",
        )
        assert p.name == "Test Student"
        assert p.skills == []
        assert p.goals == []
        assert p.gpa is None

    def test_profile_serialization(self):
        p = StudentProfile(
            name="Test",
            email="test@test.com",
            citizenship=CitizenshipStatus.US_CITIZEN,
            enrollment=EnrollmentStatus.FULL_TIME,
            major="Engineering",
            university="MIT",
            degree_level="Master",
            gpa=3.8,
            skills=["Python", "Java"],
            goals=["Get a job at Google"],
        )
        d = p.model_dump()
        assert d["name"] == "Test"
        assert d["gpa"] == 3.8

    def test_profile_extraction_result(self):
        p = StudentProfile(
            name="Test",
            email="t@t.com",
            citizenship=CitizenshipStatus.INTERNATIONAL,
            enrollment=EnrollmentStatus.FULL_TIME,
            major="CS",
            university="U",
            degree_level="Bachelor",
        )
        r = ProfileExtractionResult(
            profile=p,
            confidence=0.85,
            missing_fields=["goals"],
        )
        assert r.confidence == 0.85
        assert "goals" in r.missing_fields


class TestDeterministicMajorExtraction:
    @pytest.fixture
    def agent(self):
        return ProfileAgent()

    def test_major_not_polluted_by_next_line(self, agent):
        # The exact bug: "Major:" followed by a "GPA:" line must not bleed across.
        text = "Major: Pre-Med\nGPA: 3.7\n"
        profile = agent._extract_deterministic(text)
        assert profile.major == "Pre-Med"
        assert profile.major != "Pre-Med\nGPA"
        assert "\n" not in profile.major

    def test_demo_resume_degree_in_field_pattern(self, agent):
        # The demo résumé form: "Bachelor of Science in Pre-Med" above a GPA line.
        text = "Bachelor of Science in Pre-Med\nGPA: 3.7\n"
        profile = agent._extract_deterministic(text)
        assert profile.major == "Pre-Med"
        assert "\n" not in profile.major

    def test_multiword_same_line_major_preserved(self, agent):
        # Regression guard: a legitimate multi-word major on one line still works.
        text = "Major: Computer Science\nGPA: 3.9\n"
        profile = agent._extract_deterministic(text)
        assert profile.major == "Computer Science"

    def test_crlf_line_endings(self, agent):
        # \r\n must also be stripped, not folded into the major.
        text = "Major: Pre-Med\r\nGPA: 3.7\r\n"
        profile = agent._extract_deterministic(text)
        assert profile.major == "Pre-Med"