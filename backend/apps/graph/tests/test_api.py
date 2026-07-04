from decimal import Decimal
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from backend.apps.organizations.models import Organization, Workspace, OrganizationMember
from backend.apps.graph.models import GraphNode, GraphEdge, GraphSnapshot
from backend.apps.graph.choices import GraphNodeType, GraphRelationshipType

User = get_user_model()


class GraphAPITests(APITestCase):
    def setUp(self):
        # Create users with dummy passwords (bandit ignored)
        self.owner = User.objects.create_user(username="org_owner", email="owner@example.com", password="pass")  # nosec B106
        self.analyst = User.objects.create_user(username="analyst_user", email="analyst@example.com", password="pass")  # nosec B106
        self.other_user = User.objects.create_user(username="other_user", email="other@example.com", password="pass")  # nosec B106

        # Create Organizations
        self.org = Organization.objects.create(name="FM Org", slug="fm-org", owner=self.owner)
        self.other_org = Organization.objects.create(name="Other Org", slug="other-org", owner=self.other_user)

        # Create Workspaces
        self.workspace = Workspace.objects.create(name="FM Workspace", slug="fm-ws", organization=self.org)

        # Create Memberships
        OrganizationMember.objects.create(user=self.owner, organization=self.org, status="active", role="owner")
        OrganizationMember.objects.create(user=self.analyst, organization=self.org, status="active", role="member")
        OrganizationMember.objects.create(user=self.other_user, organization=self.other_org, status="active", role="owner")

        # Pre-seed graph nodes/edges
        self.node_a = GraphNode.objects.create(
            tenant_id=self.org.id,
            organization=self.org,
            workspace=self.workspace,
            label="Node A",
            node_type=GraphNodeType.IDENTITY,
            confidence=Decimal("1.000"),
            owner=self.owner,
        )
        self.node_b = GraphNode.objects.create(
            tenant_id=self.org.id,
            organization=self.org,
            workspace=self.workspace,
            label="Node B",
            node_type=GraphNodeType.EVIDENCE,
            confidence=Decimal("0.900"),
            owner=self.owner,
        )
        self.edge = GraphEdge.objects.create(
            tenant_id=self.org.id,
            source_node=self.node_a,
            target_node=self.node_b,
            relationship_type=GraphRelationshipType.CORRELATES_WITH,
            confidence=Decimal("0.850"),
            owner=self.owner,
        )

    def test_list_nodes_and_edges(self):
        # Authenticate analyst
        self.client.force_authenticate(user=self.analyst)

        # Retrieve nodes
        response = self.client.get("/api/v1/graph/nodes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # Retrieve edges
        response = self.client.get("/api/v1/graph/edges/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_neighborhood_expansion_and_shortest_path_api(self):
        self.client.force_authenticate(user=self.analyst)

        # Neighbor expand
        response = self.client.get("/api/v1/graph/traversal/expand/", {"node_id": str(self.node_a.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["visited_nodes"]), 2)

        # Shortest path
        response = self.client.get(
            "/api/v1/graph/traversal/shortest-path/",
            {"start_node_id": str(self.node_a.id), "end_node_id": str(self.node_b.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_cytoscape_visualization_api(self):
        self.client.force_authenticate(user=self.analyst)

        response = self.client.get("/api/v1/graph/traversal/visualize/cytoscape/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("elements", response.data)
        self.assertEqual(len(response.data["elements"]["nodes"]), 2)
        self.assertEqual(len(response.data["elements"]["edges"]), 1)

    def test_tenant_isolation_boundary(self):
        # Authenticate other_user (from other_org)
        self.client.force_authenticate(user=self.other_user)

        # Listing nodes should return empty or filter by other_user's org
        response = self.client.get("/api/v1/graph/nodes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

        # Accessing org's node directly should fail permission checks
        response = self.client.get(f"/api/v1/graph/nodes/{self.node_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
