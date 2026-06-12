from app.agents.base import BaseAgent
from app.state.session_state import SessionState
from app.models.opportunity import Opportunity, DiscoveryResult, OpportunityType
from app.llm import get_llm_or_none, parse_json_response
from typing import Any
import json


class DiscoveryAgent(BaseAgent):
    name = "DiscoveryAgent"
    description = "Finds scholarships and internships matching student profile"

    async def run(self, state: SessionState) -> dict[str, Any]:
        profile = state.get("profile")
        if not profile:
            return self.error("No profile available for discovery")

        first_name = profile.name.split()[0] if profile.name and profile.name != "Unknown" else "this student"

        narration = []
        narration.append(f"🔍 Searching scholarships and internships that match {first_name}'s goals...")

        queries = self._build_search_queries(profile)
        narration.append(f"🧭 Prioritizing {profile.major} opportunities suited to {first_name}'s strengths and ambitions...")

        opportunities = await self._search_opportunities(profile, queries, narration)

        narration.append(f"📥 Surfaced {len(opportunities)} promising opportunities to review...")
        narration.append(f"🎓 {sum(1 for o in opportunities if o.type == OpportunityType.SCHOLARSHIP)} scholarships identified...")
        narration.append(f"💼 {sum(1 for o in opportunities if o.type == OpportunityType.INTERNSHIP)} internships identified...")

        result = DiscoveryResult(
            opportunities=opportunities,
            total_found=len(opportunities),
            search_queries_used=queries,
            narration=narration,
        )

        return {
            "discovery_result": result,
            "opportunities": opportunities,
            "phase": "eligibility",
            "narration": narration,
        }

    def _build_search_queries(self, profile) -> list[str]:
        queries = []
        if profile.major:
            queries.append(f"{profile.major} scholarship")
            queries.append(f"{profile.major} internship")
        if profile.citizenship.value == "international":
            queries.append("international student scholarship")
        if profile.degree_level:
            queries.append(f"{profile.degree_level} scholarship")
        if profile.skills:
            top_skills = profile.skills[:3]
            queries.append(f"{' '.join(top_skills)} internship")
        return queries or ["general scholarship", "general internship"]

    async def _search_opportunities(self, profile, queries: list[str], narration: list) -> list[Opportunity]:
        from app.knowledge.opportunity_store import OpportunityStore
        store = OpportunityStore()

        kb_results = store.search_by_profile(profile)

        llm = get_llm_or_none()
        if llm and len(kb_results) < 5:
            narration.append("🔎 Digging deeper to surface additional strong matches...")
            llm_results = await self._llm_augmented_search(llm, profile, queries)
            kb_results.extend(llm_results)
        elif not llm and len(kb_results) < 3:
            narration.append("📚 Drawing on a curated library of vetted opportunities...")

        return kb_results

    async def _llm_augmented_search(self, llm, profile, queries: list[str]) -> list[Opportunity]:
        prompt = f"""Based on this student profile, suggest 5 real scholarships or internships they should apply for.
Student: {profile.major} major, {profile.citizenship.value} citizen, {profile.degree_level} student at {profile.university}.
Skills: {', '.join(profile.skills[:5]) if profile.skills else 'N/A'}
Goals: {', '.join(profile.goals[:3]) if profile.goals else 'N/A'}

Return a JSON array with this schema:
[{{"title": "string", "type": "scholarship|internship", "organization": "string", "amount": "string or null", 
"deadline": "YYYY-MM-DD or null", "location": "string or null", "description": "string",
"requirements": ["string"], "citizenship_requirements": ["string"], "gpa_requirement": float or null,
"degree_levels": ["string"], "fields_of_study": ["string"], "skills_required": ["string"]}}]

Return ONLY valid JSON array. Make opportunities realistic and relevant."""

        response = await llm.ainvoke(prompt)

        try:
            data = parse_json_response(response.content)
            opportunities = []
            for i, item in enumerate(data[:10]):
                opportunities.append(Opportunity(
                    id=f"llm_{i+1}",
                    type=OpportunityType(item.get("type", "scholarship")),
                    source="llm_search",
                    tags=["llm_discovered"],
                    **{k: v for k, v in item.items() if k != "type"},
                ))
            return opportunities
        except Exception:
            return []