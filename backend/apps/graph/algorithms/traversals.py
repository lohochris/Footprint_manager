from collections import deque
from typing import Any
from backend.apps.graph.dtos import EdgeDTO, NodeDTO, TraversalResultDTO


def build_adjacency_list(
    nodes: list[NodeDTO],
    edges: list[EdgeDTO],
) -> dict[str, list[tuple[str, EdgeDTO]]]:
    """Helper to build an adjacency list: node_id -> list of (neighbor_id, EdgeDTO)."""
    adj: dict[str, list[tuple[str, EdgeDTO]]] = {n.id: [] for n in nodes}
    for edge in edges:
        if edge.source_id in adj and edge.target_id in adj:
            adj[edge.source_id].append((edge.target_id, edge))
            # If undirected, add reverse direction
            if edge.direction == "undirected":
                adj[edge.target_id].append((edge.source_id, edge))
    return adj


def find_neighborhood(
    nodes: list[NodeDTO],
    edges: list[EdgeDTO],
    start_node_id: str,
    max_depth: int = 1,
    max_nodes: int = 5000,
) -> TraversalResultDTO:
    """Find neighboring nodes up to max_depth using BFS."""
    node_map = {n.id: n for n in nodes}
    if start_node_id not in node_map:
        return TraversalResultDTO(visited_nodes=[], visited_edges=[], depth=0)

    adj = build_adjacency_list(nodes, edges)

    visited_nodes: dict[str, NodeDTO] = {start_node_id: node_map[start_node_id]}
    visited_edges: list[EdgeDTO] = []

    # Queue contains tuples of (node_id, current_depth)
    queue: deque[tuple[str, int]] = deque([(start_node_id, 0)])

    while queue:
        curr_id, depth = queue.popleft()

        if depth >= max_depth:
            continue

        for neighbor_id, edge in adj.get(curr_id, []):
            if neighbor_id not in visited_nodes:
                if len(visited_nodes) >= max_nodes:
                    break
                visited_nodes[neighbor_id] = node_map[neighbor_id]
                queue.append((neighbor_id, depth + 1))

            # Include edge if not already captured
            if edge not in visited_edges:
                visited_edges.append(edge)

    return TraversalResultDTO(
        visited_nodes=list(visited_nodes.values()),
        visited_edges=visited_edges,
        depth=max_depth,
        statistics={
            "total_visited_nodes": len(visited_nodes),
            "total_visited_edges": len(visited_edges),
        },
    )


def find_shortest_path(
    nodes: list[NodeDTO],
    edges: list[EdgeDTO],
    start_id: str,
    end_id: str,
) -> list[NodeDTO]:
    """Find the shortest path of NodeDTOs between start_id and end_id using BFS."""
    node_map = {n.id: n for n in nodes}
    if start_id not in node_map or end_id not in node_map:
        return []

    if start_id == end_id:
        return [node_map[start_id]]

    adj = build_adjacency_list(nodes, edges)

    # Queue of paths: queue contains list of node_ids representing path
    queue: deque[list[str]] = deque([[start_id]])
    visited = {start_id}

    while queue:
        path = queue.popleft()
        last_id = path[-1]

        if last_id == end_id:
            return [node_map[nid] for nid in path]

        for neighbor_id, _ in adj.get(last_id, []):
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                new_path = list(path)
                new_path.append(neighbor_id)
                queue.append(new_path)

    return []  # No path found
