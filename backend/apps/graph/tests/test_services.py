from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from backend.apps.organizations.models import Organization, Workspace, OrganizationMember
from backend.apps.identity.choices import IdentityType, IdentitySource
from backend.apps.identity.models import Identity, IdentityRelationship
from backend.apps.evidence.models.evidence import Evidence
from backend.apps.investigations.models.investigation import Investigation
from backend.apps.osint.models.discovery_result import DiscoveryResult
from backend.apps.graph.models import GraphNode, GraphEdge
from backend.apps.graph.services.graph_service import GraphService
from backend.apps.graph.choices import GraphNodeType, GraphRelationshipType

User = get_user_model()


class GraphServiceTests(TestCase):
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
        self.other_workspace = Workspace.objects.create(name="Other Workspace", slug="other-ws", organization=self.other_org)

        # Create Memberships
        OrganizationMember.objects.create(user=self.owner, organization=self.org, status="active", role="owner")
        OrganizationMember.objects.create(user=self.analyst, organization=self.org, status="active", role="member")
        OrganizationMember.objects.create(user=self.other_user, organization=self.other_org, status="active", role="owner")

        # Create some source entities to build the graph from
        self.identity_a = Identity.objects.create(
            tenant_id=self.org.id,
            organization=self.org,
            workspace=self.workspace,
            label="Entity A",
            entity_type=IdentityType.PERSON,
            confidence_score=Decimal("1.000"),
            source=IdentitySource.MANUAL,
            owner=self.owner,
        )
        self.identity_b = Identity.objects.create(
            tenant_id=self.org.id,
            organization=self.org,
            workspace=self.workspace,
            label="Entity B",
            entity_type=IdentityType.EMAIL,
            confidence_score=Decimal("0.950"),
            source=IdentitySource.MANUAL,
            owner=self.owner,
        )
        self.rel = IdentityRelationship.objects.create(
            tenant_id=self.org.id,
            source_identity=self.identity_a,
            target_identity=self.identity_b,
            type=GraphRelationshipType.CORRELATES_WITH,
            confidence=Decimal("0.850"),
            owner=self.owner,
        )

        self.investigation = Investigation.objects.create(
            organization=self.org,
            workspace=self.workspace,
            title="Sovereign Shield",
            status="active",
            created_by=self.owner,
            owner=self.owner,
        )

        self.evidence = Evidence.objects.create(
            tenant_id=self.org.id,
            organization=self.org,
            workspace=self.workspace,
            title="Phishing Email Headers",
            status="verified",
            owner=self.owner,
        )

        # OSINT results
        from backend.apps.osint.models.discovery_provider import DiscoveryProvider
        from backend.apps.osint.models.discovery_job import DiscoveryJob

        provider = DiscoveryProvider.objects.create(
            name="test-provider",
            display_name="Test Provider",
            provider_status="active"
        )
        job = DiscoveryJob.objects.create(
            investigation=self.investigation,
            provider=provider,
            status="completed"
        )
        self.osint_result = DiscoveryResult.objects.create(
            job=job,
            provider=provider,
            result_type="email",
            title="osint@example.com",
            raw_data={},
        )

    def test_build_and_query_graph(self):
        # 1. Build the graph for the workspace
        res = GraphService.build_graph(self.owner, self.org, self.workspace.id)
        self.assertEqual(res["node_count"], 5)  # 2 Identities + 1 Investigation + 1 Evidence + 1 OSINT
        self.assertEqual(res["edge_count"], 1)  # 1 Relationship

        # Check DB instances
        self.assertEqual(GraphNode.objects.filter(tenant_id=self.org.id).count(), 5)
        self.assertEqual(GraphEdge.objects.filter(tenant_id=self.org.id).count(), 1)

        # 2. Query statistics
        stats = GraphService.get_statistics(self.org, self.workspace.id)
        self.assertEqual(stats.node_count, 5)
        self.assertEqual(stats.edge_count, 1)
        self.assertEqual(stats.isolated_nodes, 3)

        # 3. Expand neighborhood
        neighbors = GraphService.expand_neighborhood(self.org, self.workspace.id, str(self.identity_a.id), depth=1)
        self.assertEqual(len(neighbors.visited_nodes), 2)  # A and B

        # 4. Shortest path
        path = GraphService.get_shortest_path(self.org, self.workspace.id, str(self.identity_a.id), str(self.identity_b.id))
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0].id, str(self.identity_a.id))
        self.assertEqual(path[1].id, str(self.identity_b.id))

    def test_sync_and_refresh_graph(self):
        # Build first
        GraphService.build_graph(self.owner, self.org, self.workspace.id)

        # Incremental Sync
        new_node_id = "490807b5-2244-4860-93bf-85f02f06c11b"
        new_edge_id = "5a0a38e8-d102-4113-90bd-fbfb732bc00b"
        nodes = [
            {
                "id": new_node_id,
                "label": "Synced Custom Node",
                "node_type": "custom",
                "confidence": "0.900",
                "metadata": {"type": "IP"},
            }
        ]
        edges = [
            {
                "id": new_edge_id,
                "source_id": str(self.identity_a.id),
                "target_id": new_node_id,
                "relationship_type": "custom",
                "confidence": "0.750",
            }
        ]

        GraphService.sync_graph(self.owner, self.org, nodes, edges, self.workspace.id)

        self.assertEqual(GraphNode.objects.filter(id=new_node_id).count(), 1)
        self.assertEqual(GraphEdge.objects.filter(id=new_edge_id).count(), 1)

        # Refresh (Clears and rebuilds from source tables)
        GraphService.refresh_graph(self.owner, self.org, self.workspace.id)
        # Synced Node should be gone because it wasn't in the source DB models
        self.assertEqual(GraphNode.objects.filter(id=new_node_id).count(), 0)
        self.assertEqual(GraphNode.objects.filter(tenant_id=self.org.id).count(), 5)
