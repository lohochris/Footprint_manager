from decimal import Decimal
from typing import Any
from backend.apps.graph.dtos import EdgeDTO, GraphStatsDTO, NodeDTO


def calculate_degrees(
    nodes: list[NodeDTO],
    edges: list[EdgeDTO],
) -> dict[str, dict[str, int]]:
    """Calculate in-degree, out-degree, and total degree for all nodes."""
    degrees: dict[str, dict[str, int]] = {
        n.id: {"in": 0, "out": 0, "total": 0} for n in nodes
    }

    for edge in edges:
        if edge.source_id in degrees:
            degrees[edge.source_id]["out"] += 1
            degrees[edge.source_id]["total"] += 1
        if edge.target_id in degrees:
            degrees[edge.target_id]["in"] += 1
            degrees[edge.target_id]["total"] += 1

    return degrees


def find_connected_components(
    nodes: list[NodeDTO],
    edges: list[EdgeDTO],
) -> list[list[str]]:
    """Find all connected components (subgraphs) as lists of node IDs."""
    node_ids = {n.id for n in nodes}
    visited = set()
    components = []

    # Adjacency list for undirected traversal
    adj: dict[str, set[str]] = {n.id: set() for n in nodes}
    for edge in edges:
        if edge.source_id in adj and edge.target_id in adj:
            adj[edge.source_id].add(edge.target_id)
            adj[edge.target_id].add(edge.source_id)

    for node_id in node_ids:
        if node_id not in visited:
            component = []
            queue = [node_id]
            visited.add(node_id)

            while queue:
                curr = queue.pop(0)
                component.append(curr)

                for neighbor in adj.get(curr, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            components.append(component)

    return components


def calculate_graph_stats(
    nodes: list[NodeDTO],
    edges: list[EdgeDTO],
) -> GraphStatsDTO:
    """Generate overall summary statistics for the graph."""
    node_count = len(nodes)
    edge_count = len(edges)

    if node_count == 0:
        return GraphStatsDTO(
            node_count=0,
            edge_count=0,
            density=Decimal("0.000"),
            average_degree=Decimal("0.000"),
            isolated_nodes=0,
            largest_component_size=0,
        )

    # Calculate average degree
    total_degree = edge_count * 2
    avg_degree = Decimal(str(round(total_degree / node_count, 3)))

    # Calculate density: edges / max possible edges
    # For directed graphs, max possible = N * (N - 1)
    if node_count > 1:
        max_possible_edges = node_count * (node_count - 1)
        density = Decimal(str(round(edge_count / max_possible_edges, 3)))
    else:
        density = Decimal("0.000")

    # Find isolated nodes & largest component
    components = find_connected_components(nodes, edges)
    isolated_nodes = sum(1 for c in components if len(c) == 1)
    largest_comp_size = max(len(c) for c in components) if components else 0

    return GraphStatsDTO(
        node_count=node_count,
        edge_count=edge_count,
        density=density,
        average_degree=avg_degree,
        isolated_nodes=isolated_nodes,
        largest_component_size=largest_comp_size,
    )
