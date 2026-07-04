from decimal import Decimal
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model

from backend.apps.organizations.models import Organization, Workspace, OrganizationMember
from backend.apps.identity.choices import IdentityType, ReviewStatus, MergeAction, IdentitySource
from backend.apps.identity.models import (
    Identity,
    IdentityAttribute,
    IdentityRelationship,
    IdentityMatch,
    IdentityMergeHistory,
)
from backend.apps.identity.services.identity_service import IdentityService
from backend.apps.identity.services.matching import levenshtein_similarity

User = get_user_model()


class IdentityServiceTests(TestCase):
    def setUp(self):
        # Create users
        self.owner = User.objects.create_user(username="org_owner", email="owner@example.com", password="pass")  # nosec B106
        self.analyst = User.objects.create_user(username="analyst_user", email="analyst@example.com", password="pass")  # nosec B106
        self.other_user = User.objects.create_user(username="other_user", email="other@example.com", password="pass")  # nosec B106

        # Create Organizations
        self.org = Organization.objects.create(name="FM Org", slug="fm-org", owner=self.owner)
        self.other_org = Organization.objects.create(name="Other Org", slug="other-org", owner=self.other_user)

        # Create Workspaces
        self.workspace = Workspace.objects.create(name="FM Workspace", slug="fm-ws", organization=self.org)

        # Register users in organization
        OrganizationMember.objects.create(organization=self.org, user=self.owner, status="active")
        OrganizationMember.objects.create(organization=self.org, user=self.analyst, status="active")
        OrganizationMember.objects.create(organization=self.other_org, user=self.other_user, status="active")

    def test_resolve_identity_success(self):
        # Resolve a new person identity
        identity = IdentityService.resolve_identity(
            user=self.analyst,
            tenant=self.org,
            label="John Doe",
            entity_type=IdentityType.PERSON,
            source=IdentitySource.MANUAL,
            workspace_id=self.workspace.id,
            attributes=[
                {"type": "email", "key": "email", "value": "john.doe@example.com", "confidence": "0.950"},
            ],
        )

        self.assertIsNotNone(identity)
        self.assertEqual(identity.label, "John Doe")
        self.assertEqual(identity.entity_type, IdentityType.PERSON)
        self.assertEqual(identity.attributes.count(), 1)
        self.assertEqual(identity.attributes.first().value, "john.doe@example.com")

    def test_duplicate_discovery_and_merge_workflow(self):
        # Resolve identity 1
        id1 = IdentityService.resolve_identity(
            user=self.analyst,
            tenant=self.org,
            label="John Doe",
            entity_type=IdentityType.PERSON,
            source=IdentitySource.MANUAL,
            workspace_id=self.workspace.id,
            attributes=[
                {"type": "email", "key": "email", "value": "john.doe@example.com", "confidence": "1.000"},
            ],
        )

        # Resolve identity 2 (potential duplicate)
        id2 = IdentityService.resolve_identity(
            user=self.analyst,
            tenant=self.org,
            label="Johnathan Doe",
            entity_type=IdentityType.PERSON,
            source=IdentitySource.OSINT,
            workspace_id=self.workspace.id,
            attributes=[
                {"type": "email", "key": "email", "value": "john.doe@example.com", "confidence": "0.800"},
            ],
        )

        # Verify that a duplicate match candidate was created
        matches = IdentityMatch.objects.filter(candidate_a=id2, candidate_b=id1)
        self.assertTrue(matches.exists())
        match = matches.first()
        self.assertGreater(match.confidence, Decimal("0.500"))

        # Merge them
        master = IdentityService.merge_identities(
            user=self.analyst,
            tenant=self.org,
            identity_a_id=id1.id,
            identity_b_id=id2.id,
        )

        # Verify merged state
        self.assertEqual(master.id, id1.id)  # id1 should be kept (higher confidence)
        id2_reloaded = Identity.objects.get(id=id2.id)
        self.assertTrue(id2_reloaded.is_deleted)

        # Attributes should have been moved
        self.assertEqual(master.attributes.count(), 2)

        # Verify history record
        histories = IdentityMergeHistory.objects.filter(target_identity=master)
        self.assertTrue(histories.exists())
        history = histories.first()
        self.assertEqual(history.action, MergeAction.MERGE)
        self.assertEqual(history.source_identity_id, id2.id)

        # Split them back
        restored_master = IdentityService.split_identity(
            user=self.analyst,
            tenant=self.org,
            merge_history_id=history.id,
        )

        # Verify split state
        id2_split = Identity.objects.get(id=id2.id)
        self.assertFalse(id2_split.is_deleted)
        self.assertEqual(restored_master.attributes.count(), 1)
        self.assertEqual(id2_split.attributes.count(), 1)
