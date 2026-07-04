import abc
import xml.etree.ElementTree as ET  # nosec B405
from typing import Any, Generator
from django.db.models import QuerySet
from backend.apps.identity.models import Identity, IdentityRelationship


class GraphExporter(abc.ABC):
    """Abstract Interface for exporting Identity Graph structures."""

    @abc.abstractmethod
    def export_adjacency_list(self, identities: QuerySet[Identity]) -> dict[str, list[dict[str, Any]]]:
        """Convert identities and their relationships to an adjacency list format."""
        pass

    @abc.abstractmethod
    def export_graphml(self, identities: QuerySet[Identity]) -> Generator[str, None, None]:
        """Stream the identity graph structure in GraphML format."""
        pass

    @abc.abstractmethod
    def export_json_nodes_edges(self, identities: QuerySet[Identity]) -> dict[str, list[dict[str, Any]]]:
        """Serialize nodes and edges for client-side rendering (e.g., vis.js or D3)."""
        pass


class DjangoModelGraphExporter(GraphExporter):
    """Concrete implementation of GraphExporter utilizing Django ORM models."""

    def export_adjacency_list(self, identities: QuerySet[Identity]) -> dict[str, list[dict[str, Any]]]:
        identity_ids = list(identities.values_list("id", flat=True))
        relationships = IdentityRelationship.objects.filter(
            source_identity_id__in=identity_ids,
            target_identity_id__in=identity_ids,
        )

        adj_list: dict[str, list[dict[str, Any]]] = {str(i_id): [] for i_id in identity_ids}

        for rel in relationships:
            adj_list[str(rel.source_identity_id)].append({
                "target_id": str(rel.target_identity_id),
                "type": rel.type,
                "confidence": str(rel.confidence),
                "source": rel.source,
            })

        return adj_list

    def export_graphml(self, identities: QuerySet[Identity]) -> Generator[str, None, None]:
        identity_ids = list(identities.values_list("id", flat=True))
        relationships = IdentityRelationship.objects.filter(
            source_identity_id__in=identity_ids,
            target_identity_id__in=identity_ids,
        )

        root = ET.Element("graphml", {
            "xmlns": "http://graphml.graphdrawing.org/xmlns",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
        })
        graph = ET.SubElement(root, "graph", {"id": "G", "edgedefault": "directed"})

        # Add key descriptions
        ET.SubElement(root, "key", {"id": "d0", "for": "node", "attr.name": "label", "attr.type": "string"})
        ET.SubElement(root, "key", {"id": "d1", "for": "node", "attr.name": "entity_type", "attr.type": "string"})
        ET.SubElement(root, "key", {"id": "d2", "for": "edge", "attr.name": "relation_type", "attr.type": "string"})

        for identity in identities:
            node = ET.SubElement(graph, "node", {"id": str(identity.id)})
            d_lbl = ET.SubElement(node, "data", {"key": "d0"})
            d_lbl.text = identity.label
            d_typ = ET.SubElement(node, "data", {"key": "d1"})
            d_typ.text = identity.entity_type

        for rel in relationships:
            edge = ET.SubElement(graph, "edge", {
                "id": str(rel.id),
                "source": str(rel.source_identity_id),
                "target": str(rel.target_identity_id),
            })
            d_rel = ET.SubElement(edge, "data", {"key": "d2"})
            d_rel.text = rel.type

        # Serialize element by element to support streaming (generator)
        xml_str = ET.tostring(root, encoding="utf-8").decode("utf-8")
        yield xml_str

    def export_json_nodes_edges(self, identities: QuerySet[Identity]) -> dict[str, list[dict[str, Any]]]:
        identity_ids = list(identities.values_list("id", flat=True))
        relationships = IdentityRelationship.objects.filter(
            source_identity_id__in=identity_ids,
            target_identity_id__in=identity_ids,
        )

        nodes = []
        for identity in identities:
            nodes.append({
                "id": str(identity.id),
                "label": identity.label,
                "entity_type": identity.entity_type,
                "confidence_score": str(identity.confidence_score),
            })

        edges = []
        for rel in relationships:
            edges.append({
                "id": str(rel.id),
                "source": str(rel.source_identity_id),
                "target": str(rel.target_identity_id),
                "type": rel.type,
                "confidence": str(rel.confidence),
            })

        return {
            "nodes": nodes,
            "edges": edges,
        }
