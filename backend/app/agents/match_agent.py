from app.agents.base import BaseAgent
from app.state.session_state import SessionState
from app.models.match import MatchResult, RankedOpportunity
from app.config import reference_today
from typing import Any


class MatchAgent(BaseAgent):
    name = "MatchAgent"
    description = "Ranks opportunities by match score using weighted formula"

    WEIGHTS = {
        "eligibility": 0.30,
        "academic_fit": 0.25,
        "goals_fit": 0.20,
        "skills_fit": 0.15,
        "urgency": 0.10,
    }

    async def run(self, state: SessionState) -> dict[str, Any]:
        profile = state.get("profile")
        opportunities = state.get("opportunities", [])
        eligibility_results = state.get("eligibility_results", [])

        if not profile or not opportunities:
            return self.error("Missing profile or opportunities for matching")

        first_name = profile.name.split()[0] if profile.name and profile.name != "Unknown" else "this student"

        narration = []
        narration.append("✨ Weighing each opportunity by fit, goals, and urgency...")

        elig_map = {r.opportunity_id: r for r in eligibility_results}
        ranked = []

        for opp in opportunities:
            elig = elig_map.get(opp.id)
            elig_score = elig.score if elig else 0.0
            elig_verdict = elig.verdict.value if elig else "not_eligible"

            academic_fit = self._score_academic_fit(profile, opp)
            goals_fit = self._score_goals_fit(profile, opp)
            skills_fit = self._score_skills_fit(profile, opp)
            urgency = self._score_urgency(opp)

            match_score = (
                self.WEIGHTS["eligibility"] * elig_score
                + self.WEIGHTS["academic_fit"] * academic_fit
                + self.WEIGHTS["goals_fit"] * goals_fit
                + self.WEIGHTS["skills_fit"] * skills_fit
                + self.WEIGHTS["urgency"] * urgency
            )

            ranked.append(RankedOpportunity(
                opportunity_id=opp.id,
                title=opp.title,
                organization=opp.organization,
                type=opp.type.value,
                match_score=round(match_score, 3),
                eligibility_score=round(elig_score, 3),
                academic_fit=round(academic_fit, 3),
                goals_fit=round(goals_fit, 3),
                skills_fit=round(skills_fit, 3),
                urgency=round(urgency, 3),
                eligibility_verdict=elig_verdict,
                deadline=str(opp.deadline) if opp.deadline else None,
            ))

        ranked.sort(key=lambda x: x.match_score, reverse=True)
        
        top_picks = [r for r in ranked if r.eligibility_verdict != "not_eligible"][:5]
        
        strong = sum(1 for r in ranked if r.eligibility_verdict != "not_eligible")
        narration.append(f"🏆 Top recommendation: {ranked[0].title} — {ranked[0].match_score:.0%} fit." if ranked else "🤔 No eligible matches yet — a broader search may surface more.")
        narration.append(f"✨ Prioritized {strong} strong matches by fit and urgency for {first_name}.")

        result = MatchResult(
            ranked_opportunities=ranked,
            top_picks=top_picks,
            narration=narration,
        )

        return {
            "match_result": result,
            "phase": "ready",
            "narration": narration,
        }

    def _score_academic_fit(self, profile, opp) -> float:
        score = 0.5
        if opp.fields_of_study:
            major_lower = profile.major.lower()
            if any(f.lower() in major_lower or major_lower in f.lower() for f in opp.fields_of_study):
                score += 0.5
        if opp.degree_levels:
            if any(profile.degree_level.lower() in d.lower() for d in opp.degree_levels):
                score += 0.3
        if opp.gpa_requirement and profile.gpa:
            if profile.gpa >= opp.gpa_requirement + 0.3:
                score += 0.2
        return min(score, 1.0)

    def _score_goals_fit(self, profile, opp) -> float:
        if not profile.goals:
            return 0.5
        desc_lower = opp.description.lower()
        matches = sum(1 for g in profile.goals if any(w in desc_lower for w in g.lower().split()))
        return min(matches / max(len(profile.goals), 1) + 0.3, 1.0)

    def _score_skills_fit(self, profile, opp) -> float:
        if not opp.skills_required or not profile.skills:
            return 0.5
        required = set(s.lower() for s in opp.skills_required)
        have = set(s.lower() for s in profile.skills)
        if not required:
            return 0.7
        overlap = len(required & have)
        return min(overlap / len(required) + 0.2, 1.0)

    def _score_urgency(self, opp) -> float:
        if not opp.deadline:
            return 0.5
        days = (opp.deadline - reference_today()).days
        if days < 0:
            return 0.0
        elif days < 7:
            return 1.0
        elif days < 30:
            return 0.8
        elif days < 90:
            return 0.5
        else:
            return 0.3