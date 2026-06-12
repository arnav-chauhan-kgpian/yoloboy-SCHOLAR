import pytest
from app.models.match import MatchResult, RankedOpportunity
from app.agents.match_agent import MatchAgent
from app.models.profile import StudentProfile, CitizenshipStatus, EnrollmentStatus
from app.models.opportunity import Opportunity, OpportunityType
from datetime import date, timedelta
from app.config import reference_today


class TestMatchModels:
    def test_ranked_opportunity(self):
        r = RankedOpportunity(
            opportunity_id="1",
            title="Test",
            organization="Org",
            type="scholarship",
            match_score=0.85,
            eligibility_score=1.0,
            academic_fit=0.8,
            goals_fit=0.7,
            skills_fit=0.6,
            urgency=0.5,
            eligibility_verdict="eligible",
        )
        assert r.match_score == 0.85

    def test_match_agent_weights(self):
        assert MatchAgent.WEIGHTS["eligibility"] == 0.30
        assert MatchAgent.WEIGHTS["academic_fit"] == 0.25


class TestMatchAgent:
    @pytest.fixture
    def agent(self):
        return MatchAgent()

    @pytest.fixture
    def profile(self):
        return StudentProfile(
            name="Test",
            email="t@t.com",
            citizenship=CitizenshipStatus.US_CITIZEN,
            enrollment=EnrollmentStatus.FULL_TIME,
            major="Computer Science",
            university="MIT",
            degree_level="Bachelor",
            gpa=3.9,
            skills=["Python", "Java", "Algorithms"],
            goals=["Work at a top tech company"],
        )

    def test_score_academic_fit_matching(self, agent, profile):
        opp = Opportunity(
            id="t1",
            title="CS Scholarship",
            type=OpportunityType.SCHOLARSHIP,
            organization="Org",
            description="CS scholarship",
            fields_of_study=["Computer Science"],
            degree_levels=["Bachelor"],
        )
        score = agent._score_academic_fit(profile, opp)
        assert score >= 0.8

    def test_score_academic_fit_non_matching(self, agent, profile):
        opp = Opportunity(
            id="t2",
            title="Art Scholarship",
            type=OpportunityType.SCHOLARSHIP,
            organization="Org",
            description="Art",
            fields_of_study=["Fine Arts"],
            degree_levels=["Bachelor"],
        )
        score = agent._score_academic_fit(profile, opp)
        assert score == 0.8  # base 0.5 + degree level match 0.3, no field match

    def test_score_urgency_urgent(self, agent, profile):
        opp = Opportunity(
            id="t3",
            title="Urgent",
            type=OpportunityType.SCHOLARSHIP,
            organization="Org",
            description="",
            deadline=reference_today() + timedelta(days=3),
        )
        score = agent._score_urgency(opp)
        assert score == 1.0

    def test_score_urgency_past(self, agent, profile):
        opp = Opportunity(
            id="t4",
            title="Expired",
            type=OpportunityType.SCHOLARSHIP,
            organization="Org",
            description="",
            deadline=reference_today() - timedelta(days=1),
        )
        score = agent._score_urgency(opp)
        assert score == 0.0