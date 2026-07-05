import pytest
import uuid
from decimal import Decimal
from backend.apps.graph.dtos import NodeDTO, EdgeDTO
from backend.apps.intelligence.providers.analytics import AnalyticsProvider

def test_analytics_empty_graph():
    provider = AnalyticsProvider()
    result = provider.calculate("tenant_1", "workspace_1", [], [])

    assert result.tenant_id == "tenant_1"
    assert result.statistics["node_count"] == 0
    assert result.statistics["edge_count"] == 0
    assert len(result.node_metrics) == 0

def test_analytics_isolated_nodes():
    provider = AnalyticsProvider()
    node1 = NodeDTO(id=uuid.uuid4(), tenant_id="t1", workspace_id="w1", node_type="entity", label="Person", metadata={})
    node2 = NodeDTO(id=uuid.uuid4(), tenant_id="t1", workspace_id="w1", node_type="entity", label="Person", metadata={})

    result = provider.calculate("tenant_1", "workspace_1", [node1, node2], [])

    assert result.statistics["node_count"] == 2
    assert result.statistics["component_count"] == 2
    assert result.node_metrics[node1.id].degree == Decimal("0.0")

def test_analytics_connected_graph():
    provider = AnalyticsProvider()
    node1 = NodeDTO(id=uuid.uuid4(), tenant_id="t1", workspace_id="w1", node_type="entity", label="Person", metadata={})
    node2 = NodeDTO(id=uuid.uuid4(), tenant_id="t1", workspace_id="w1", node_type="entity", label="Email", metadata={})
    node3 = NodeDTO(id=uuid.uuid4(), tenant_id="t1", workspace_id="w1", node_type="entity", label="Phone", metadata={})

    edge1 = EdgeDTO(id=uuid.uuid4(), tenant_id="t1", source_id=node1.id, target_id=node2.id, relationship_type="HAS_EMAIL")
    edge2 = EdgeDTO(id=uuid.uuid4(), tenant_id="t1", source_id=node1.id, target_id=node3.id, relationship_type="HAS_PHONE")

    result = provider.calculate("tenant_1", "workspace_1", [node1, node2, node3], [edge1, edge2])

    assert result.statistics["component_count"] == 1
    # Node 1 is connected to 2 and 3. Centrality of node 1 should be 1.0 (2 edges / 2 possible)
    assert result.node_metrics[node1.id].degree == Decimal("1.0")
    # Node 2 and 3 should have 0.5 (1 edge / 2 possible)
    assert result.node_metrics[node2.id].degree == Decimal("0.5")
    assert result.node_metrics[node3.id].degree == Decimal("0.5")

def test_analytics_cyclic_graph():
    provider = AnalyticsProvider()
    node1 = NodeDTO(id=uuid.uuid4(), tenant_id="t1", workspace_id="w1", node_type="entity", label="Person", metadata={})
    node2 = NodeDTO(id=uuid.uuid4(), tenant_id="t1", workspace_id="w1", node_type="entity", label="Person", metadata={})
    node3 = NodeDTO(id=uuid.uuid4(), tenant_id="t1", workspace_id="w1", node_type="entity", label="Person", metadata={})

    edge1 = EdgeDTO(id=uuid.uuid4(), tenant_id="t1", source_id=node1.id, target_id=node2.id, relationship_type="KNOWS")
    edge2 = EdgeDTO(id=uuid.uuid4(), tenant_id="t1", source_id=node2.id, target_id=node3.id, relationship_type="KNOWS")
    edge3 = EdgeDTO(id=uuid.uuid4(), tenant_id="t1", source_id=node3.id, target_id=node1.id, relationship_type="KNOWS")

    result = provider.calculate("tenant_1", "workspace_1", [node1, node2, node3], [edge1, edge2, edge3])

    # Fully connected triangle, all should have 1.0 degree centrality
    assert result.node_metrics[node1.id].degree == Decimal("1.0")
    assert result.node_metrics[node2.id].degree == Decimal("1.0")
    assert result.node_metrics[node3.id].degree == Decimal("1.0")
