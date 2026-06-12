import pytest
from app.models.eligibility import (
    EligibilityResult, EligibilityVerdict, EligibilityReason, EligibilityBatchResult
)
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.match_agent import MatchAgent
from app.knowledge.opportunity_store import OpportunityStore
from app.models.profile import StudentProfile, CitizenshipStatus, EnrollmentStatus
from app.models.opportunity import Opportunity, OpportunityType
from datetime import date


class TestEligibilityModels:
    def test_eligible_verdict(self):
        r = EligibilityResult(
            opportunity_id="test",
            verdict=EligibilityVerdict.ELIGIBLE,
            score=0.95,
            reasons=[EligibilityReason(requirement="X", student_value="Y", passed=True, notes="OK")],
            summary="Meets all requirements",
        )
        assert r.verdict == EligibilityVerdict.ELIGIBLE
        assert r.score == 0.95

    def test_batch_counts(self):
        batch = EligibilityBatchResult(
            results=[
                EligibilityResult(opportunity_id="1", verdict=EligibilityVerdict.ELIGIBLE, score=1.0),
                EligibilityResult(opportunity_id="2", verdict=EligibilityVerdict.NOT_ELIGIBLE, score=0.0),
            ],
            eligible_count=1,
            rejected_count=1,
        )
        assert batch.eligible_count == 1
        assert batch.rejected_count == 1


class TestEligibilityAgent:
    @pytest.fixture
    def agent(self):
        return EligibilityAgent()

    @pytest.fixture
    def profile(self):
        return StudentProfile(
            name="Test",
            email="t@t.com",
            citizenship=CitizenshipStatus.INTERNATIONAL,
            enrollment=EnrollmentStatus.FULL_TIME,
            major="Computer Science",
            university="Test U",
            degree_level="Bachelor",
            gpa=3.7,
            goals=["Research"],
        )

    @pytest.fixture
    def us_only_opportunity(self):
        return Opportunity(
            id="test_us",
            title="US Only Scholarship",
            type=OpportunityType.SCHOLARSHIP,
            organization="US Gov",
            description="For US citizens only",
            requirements=["US Citizenship"],
            citizenship_requirements=["US Citizen"],
        )

    @pytest.fixture
    def international_friendly_opportunity(self):
        return Opportunity(
            id="test_intl",
            title="Global Scholarship",
            type=OpportunityType.SCHOLARSHIP,
            organization="Global Fund",
            description="Open to all",
            requirements=[],
        )

    def test_reject_us_only_for_international(self, agent, profile, us_only_opportunity):
        result = agent._check_eligibility(profile, us_only_opportunity)
        assert result.verdict == EligibilityVerdict.NOT_ELIGIBLE
        assert any("Citizenship" in r.requirement for r in result.reasons if not r.passed)

    def test_accept_international_friendly(self, agent, profile, international_friendly_opportunity):
        result = agent._check_eligibility(profile, international_friendly_opportunity)
        assert result.verdict == EligibilityVerdict.ELIGIBLE

    def test_reject_us_citizen_for_international_only(self, agent):
        # R2 regression: a US citizen must NOT be marked eligible for an international-only award.
        us_student = StudentProfile(
            name="Sam", email="s@s.com", citizenship=CitizenshipStatus.US_CITIZEN,
            enrollment=EnrollmentStatus.FULL_TIME, major="Computer Science",
            university="Test U", degree_level="Master", gpa=3.9,
        )
        intl_only = Opportunity(
            id="intl_only", title="International Fellowship", type=OpportunityType.SCHOLARSHIP,
            organization="Global Fund", description="For international students only",
            citizenship_requirements=["International"], degree_levels=["Master"],
        )
        result = agent._check_eligibility(us_student, intl_only)
        assert result.verdict == EligibilityVerdict.NOT_ELIGIBLE

    def test_gpa_near_miss_is_borderline(self, agent, profile):
        # 3.7 vs 3.8 (within 0.2 tolerance) → Borderline, not rejected.
        opp = Opportunity(
            id="gpa_close", title="High GPA Award", type=OpportunityType.SCHOLARSHIP,
            organization="Org", description="x", gpa_requirement=3.8,
            fields_of_study=["Computer Science"], degree_levels=["Bachelor"],
        )
        result = agent._check_eligibility(profile, opp)
        assert result.verdict == EligibilityVerdict.BORDERLINE

    def test_gpa_far_below_is_not_eligible(self, agent, profile):
        # 3.7 vs 4.5-style large gap (>0.2 tolerance) → hard reject.
        opp = Opportunity(
            id="gpa_far", title="Impossible GPA Award", type=OpportunityType.SCHOLARSHIP,
            organization="Org", description="x", gpa_requirement=4.0,
            fields_of_study=["Computer Science"], degree_levels=["Bachelor"],
        )
        result = agent._check_eligibility(profile, opp)
        assert result.verdict == EligibilityVerdict.NOT_ELIGIBLE

    def test_degree_level_mismatch_is_not_eligible(self, agent, profile):
        # Bachelor student vs PhD-only fellowship → hard reject.
        opp = Opportunity(
            id="phd_only", title="PhD Fellowship", type=OpportunityType.SCHOLARSHIP,
            organization="Org", description="x", degree_levels=["PhD"],
            fields_of_study=["Computer Science"],
        )
        result = agent._check_eligibility(profile, opp)
        assert result.verdict == EligibilityVerdict.NOT_ELIGIBLE


class TestMayaBorderlineDemo:
    """The canonical demo: Maya Chen must produce a high-quality ⚠️ Borderline
    on the Rural Health Pre-Med Excellence Scholarship (seed_101)."""

    @pytest.fixture
    def agent(self):
        return EligibilityAgent()

    @pytest.fixture
    def maya(self):
        # Mirrors the deterministic parse of the demo resume:
        # major "Pre-Med", GPA 3.7, Bachelor, international.
        return StudentProfile(
            name="Maya Chen", email="maya.chen@stanford.edu",
            citizenship=CitizenshipStatus.INTERNATIONAL, enrollment=EnrollmentStatus.FULL_TIME,
            gpa=3.7, major="Pre-Med", university="Stanford University", degree_level="Bachelor",
            skills=["Research", "Patient Care", "Public Health", "Health Education"],
            goals=[
                "Become a physician serving rural communities",
                "Passionate about reducing healthcare disparities",
                "Seeking opportunities in community medicine and public health",
            ],
        )

    @pytest.fixture
    def seed_101(self):
        return OpportunityStore().get_by_id("seed_101")

    def test_seed_101_exists(self, seed_101):
        assert seed_101 is not None
        assert seed_101.gpa_requirement == 3.8
        assert seed_101.type == OpportunityType.SCHOLARSHIP

    def test_maya_is_borderline_on_seed_101(self, agent, maya, seed_101):
        result = agent._check_eligibility(maya, seed_101)
        assert result.verdict == EligibilityVerdict.BORDERLINE

    def test_borderline_reason_is_exactly_gpa(self, agent, maya, seed_101):
        result = agent._check_eligibility(maya, seed_101)
        failed = [r for r in result.reasons if not r.passed]
        # The ONLY failing reason is the GPA, and it is soft (within tolerance).
        assert len(failed) == 1
        assert failed[0].severity == "soft"
        assert "3.8" in failed[0].requirement
        assert "3.7" in failed[0].notes
        # Every non-GPA requirement (citizenship/degree/field) passes.
        for r in result.reasons:
            if "GPA" not in r.requirement:
                assert r.passed

    def test_seed_101_in_maya_discovery_subset(self, maya):
        store = OpportunityStore()
        subset = store.search_by_profile(maya)
        assert any(o.id == "seed_101" for o in subset)

    def test_seed_101_ranks_reasonably_high(self, agent, maya):
        # Mirror the pipeline: eligibility on discovery subset, then the match formula.
        store = OpportunityStore()
        match = MatchAgent()
        subset = store.search_by_profile(maya)
        results = {o.id: agent._check_eligibility(maya, o) for o in subset}

        ranked = []
        for o in subset:
            r = results[o.id]
            if r.verdict == EligibilityVerdict.NOT_ELIGIBLE:
                continue
            score = (
                0.30 * r.score
                + 0.25 * match._score_academic_fit(maya, o)
                + 0.20 * match._score_goals_fit(maya, o)
                + 0.15 * match._score_skills_fit(maya, o)
                + 0.10 * match._score_urgency(o)
            )
            ranked.append((score, o.id))
        ranked.sort(reverse=True)

        top_ids = [oid for _, oid in ranked[:5]]
        assert "seed_101" in top_ids, f"seed_101 not in top 5: {ranked[:8]}"

    def test_all_three_verdicts_present_for_maya(self, agent, maya):
        # The whole point of the demo: Maya yields ✅, ⚠️, and ❌ together.
        store = OpportunityStore()
        subset = store.search_by_profile(maya)
        verdicts = {agent._check_eligibility(maya, o).verdict for o in subset}
        assert EligibilityVerdict.ELIGIBLE in verdicts
        assert EligibilityVerdict.BORDERLINE in verdicts
        assert EligibilityVerdict.NOT_ELIGIBLE in verdicts