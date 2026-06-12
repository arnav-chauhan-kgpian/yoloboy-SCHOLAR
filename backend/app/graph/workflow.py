from langgraph.graph import StateGraph, START, END
from app.state.session_state import SessionState
from app.agents.profile_agent import ProfileAgent
from app.agents.discovery_agent import DiscoveryAgent
from app.agents.eligibility_agent import EligibilityAgent
from app.agents.match_agent import MatchAgent
from app.agents.application_agent import ApplicationAgent
from app.agents.tracker_agent import TrackerAgent
from typing import Annotated, Any


profile_agent = ProfileAgent()
discovery_agent = DiscoveryAgent()
eligibility_agent = EligibilityAgent()
match_agent = MatchAgent()
application_agent = ApplicationAgent()
tracker_agent = TrackerAgent()


async def run_profile(state: SessionState) -> dict[str, Any]:
    return await profile_agent.run(state)


async def run_discovery(state: SessionState) -> dict[str, Any]:
    result = await discovery_agent.run(state)
    return result


async def run_eligibility(state: SessionState) -> dict[str, Any]:
    return await eligibility_agent.run(state)


async def run_matching(state: SessionState) -> dict[str, Any]:
    return await match_agent.run(state)


async def run_application(state: SessionState) -> dict[str, Any]:
    return await application_agent.run(state)


async def run_tracker(state: SessionState) -> dict[str, Any]:
    return await tracker_agent.run(state)


def route_after_profile(state: SessionState) -> str:
    return "discovery"


def route_after_discovery(state: SessionState) -> str:
    return "eligibility"


def route_after_eligibility(state: SessionState) -> str:
    return "matching"


def route_after_matching(state: SessionState) -> str:
    if state.get("application_results") or state.get("_skip_application"):
        return END
    return "application_ready"


def route_application_ready(state: SessionState) -> str:
    return "application"


def route_after_application(state: SessionState) -> str:
    return "tracker"


def route_after_tracker(state: SessionState) -> str:
    return END


def build_scholarai_graph() -> StateGraph:
    builder = StateGraph(SessionState)

    builder.add_node("profile", run_profile)
    builder.add_node("discovery", run_discovery)
    builder.add_node("eligibility", run_eligibility)
    builder.add_node("matching", run_matching)
    builder.add_node("application", run_application)
    builder.add_node("tracker", run_tracker)

    builder.add_conditional_edges("profile", route_after_profile)
    builder.add_conditional_edges("discovery", route_after_discovery)
    builder.add_conditional_edges("eligibility", route_after_eligibility)
    builder.add_conditional_edges("matching", route_after_matching, {
        END: END,
        "application_ready": "application",
    })
    builder.add_conditional_edges("application", route_after_application)
    builder.add_conditional_edges("tracker", route_after_tracker)

    builder.set_entry_point("profile")

    return builder.compile()