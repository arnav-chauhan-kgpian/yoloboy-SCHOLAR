import pytest
from app.graph.workflow import build_scholarai_graph
from app.state.session_state import SessionState


class TestOrchestrator:
    def test_graph_builds(self):
        graph = build_scholarai_graph()
        assert graph is not None

    def test_graph_nodes(self):
        graph = build_scholarai_graph()
        assert "profile" in graph.nodes
        assert "discovery" in graph.nodes
        assert "eligibility" in graph.nodes
        assert "matching" in graph.nodes
        assert "application" in graph.nodes
        assert "tracker" in graph.nodes