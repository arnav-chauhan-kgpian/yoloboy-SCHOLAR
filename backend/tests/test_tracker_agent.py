import pytest
from app.models.tracker import TrackerEntry, ActionPlan, TrackerResult
from datetime import date, timedelta


class TestTrackerModels:
    def test_tracker_entry(self):
        e = TrackerEntry(
            opportunity_id="1",
            title="Test",
            deadline=date.today() + timedelta(days=5),
            days_remaining=5,
            priority="critical",
        )
        assert e.priority == "critical"
        assert e.days_remaining == 5

    def test_action_plan_categorization(self):
        plan = ActionPlan(
            immediate=[TrackerEntry(opportunity_id="1", title="Immediate", priority="critical")],
            upcoming=[TrackerEntry(opportunity_id="2", title="Upcoming", priority="high")],
            watchlist=[TrackerEntry(opportunity_id="3", title="Watch")],
        )
        assert len(plan.immediate) == 1
        assert len(plan.upcoming) == 1
        assert plan.immediate[0].priority == "critical"