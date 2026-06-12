from app.agents.base import BaseAgent
from app.state.session_state import SessionState
from app.agents.profile_agent import ProfileAgent
from app.agents.discovery_agent import DiscoveryAgent
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.match_agent import MatchAgent
from app.agents.application_agent import ApplicationAgent
from app.agents.tracker_agent import TrackerAgent
from typing import Any


class OrchestratorAgent(BaseAgent):
    name = "OrchestratorAgent"
    description = "Coordinates all agents through LangGraph-defined control flow"

    AGENTS = {
        "profile": ProfileAgent(),
        "discovery": DiscoveryAgent(),
        "eligibility": EligibilityAgent(),
        "matching": MatchAgent(),
        "application": ApplicationAgent(),
        "tracker": TrackerAgent(),
    }

    async def run(self, state: SessionState) -> dict[str, Any]:
        phase = state.get("phase", "profile")
        agent = self.AGENTS.get(phase)
        if not agent:
            return self.error(f"Unknown phase: {phase}")
        return await agent.run(state)