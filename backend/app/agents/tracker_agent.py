from app.agents.base import BaseAgent
from app.state.session_state import SessionState
from app.models.tracker import TrackerResult, ActionPlan, TrackerEntry
from app.config import reference_today
from typing import Any


class TrackerAgent(BaseAgent):
    name = "TrackerAgent"
    description = "Creates prioritized action plans and deadline tracking"

    async def run(self, state: SessionState) -> dict[str, Any]:
        match_result = state.get("match_result")
        opportunities_map = {o.id: o for o in state.get("opportunities", [])}

        if not match_result:
            return self.error("No match results for tracking")

        narration = []
        narration.append("📅 Turning the best matches into a prioritized action plan...")

        entries = []
        for ranked in match_result.ranked_opportunities:
            opp = opportunities_map.get(ranked.opportunity_id)
            if not opp:
                continue

            days = None
            if opp.deadline:
                days = (opp.deadline - reference_today()).days

            priority = self._determine_priority(ranked, days)

            entries.append(TrackerEntry(
                opportunity_id=opp.id,
                title=opp.title,
                deadline=opp.deadline,
                status=self._determine_status(ranked, days),
                days_remaining=days,
                priority=priority,
            ))

        immediate = [e for e in entries if e.priority == "critical"]
        upcoming = [e for e in entries if e.priority == "high"]
        watchlist = [e for e in entries if e.priority in ("medium", "low")]

        narration.append(f"🚨 {len(immediate)} need attention now — deadlines are close.")
        narration.append(f"📋 {len(upcoming)} strong options to prepare next.")
        narration.append(f"👀 {len(watchlist)} more saved to keep an eye on.")

        for entry in immediate[:3]:
            narration.append(f"🔴 Apply to {entry.title} first — only {entry.days_remaining} days left.")

        result = TrackerResult(
            action_plan=ActionPlan(
                immediate=immediate,
                upcoming=upcoming,
                watchlist=watchlist,
            ),
            narration=narration,
        )

        return {
            "tracker_result": result,
            "narration": narration,
        }

    def _determine_priority(self, ranked, days_remaining) -> str:
        if days_remaining is not None and days_remaining < 7:
            return "critical"
        if ranked.eligibility_verdict == "eligible" and ranked.match_score >= 0.6:
            if days_remaining is not None and days_remaining < 30:
                return "critical"
            return "high"
        if ranked.eligibility_verdict == "borderline":
            return "medium"
        return "low"

    def _determine_status(self, ranked, days_remaining) -> str:
        if days_remaining is not None and days_remaining < 0:
            return "expired"
        if ranked.eligibility_verdict == "eligible":
            return "ready_to_apply"
        if ranked.eligibility_verdict == "borderline":
            return "needs_review"
        return "not_applicable"