import pytest
from app.models.opportunity import Opportunity, OpportunityType, DiscoveryResult
from app.knowledge.opportunity_store import OpportunityStore
from datetime import date


class TestOpportunityModels:
    def test_opportunity_creation(self):
        opp = Opportunity(
            id="test_1",
            title="Test Scholarship",
            type=OpportunityType.SCHOLARSHIP,
            organization="Test Org",
            amount="$5,000",
            deadline=date(2026, 12, 31),
            description="A test scholarship",
            requirements=["Must be a student"],
        )
        assert opp.type == OpportunityType.SCHOLARSHIP
        assert opp.amount == "$5,000"

    def test_discovery_result_counts(self):
        r = DiscoveryResult(opportunities=[], total_found=0)
        assert r.total_found == 0


class TestOpportunityStore:
    def test_store_has_seed_data(self):
        store = OpportunityStore()
        all_opps = store.get_all()
        assert len(all_opps) >= 8

    def test_search_by_query(self):
        store = OpportunityStore()
        results = store.search_by_query("Google")
        assert len(results) >= 1
        assert any("Google" in o.title or "Google" in o.organization for o in results)

    def test_get_by_id(self):
        store = OpportunityStore()
        opp = store.get_by_id("seed_001")
        assert opp is not None
        assert opp.title == "Gates Millennium Scholars Program"

    def test_get_by_id_missing(self):
        store = OpportunityStore()
        assert store.get_by_id("nonexistent") is None