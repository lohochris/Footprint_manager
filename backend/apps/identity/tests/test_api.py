from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from backend.apps.organizations.models import Organization, Workspace, OrganizationMember
from backend.apps.identity.choices import IdentityType, ReviewStatus, IdentitySource
from backend.apps.identity.models import Identity, IdentityMatch, IdentityMergeHistory

User = get_user_model()


class IdentityAPITests(APITestCase):
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

    def test_list_identities_tenant_isolation(self):
        # Create an identity for org
        Identity.objects.create(
            tenant_id=self.org.id,
            organization=self.org,
            label="John Doe",
            entity_type=IdentityType.PERSON,
            source=IdentitySource.MANUAL,
            owner=self.analyst,
        )

        # Create an identity for other_org
        Identity.objects.create(
            tenant_id=self.other_org.id,
            organization=self.other_org,
            label="Alice Smith",
            entity_type=IdentityType.PERSON,
            source=IdentitySource.MANUAL,
            owner=self.other_user,
        )

        # Login as analyst
        self.client.force_authenticate(user=self.analyst)

        # Retrieve list
        url = reverse("identity-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see John Doe
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["label"], "John Doe")

    def test_resolve_identity_api(self):
        self.client.force_authenticate(user=self.analyst)
        url = reverse("identity-list")
        data = {
            "label": "Mark Taylor",
            "entity_type": IdentityType.PERSON,
            "source": IdentitySource.OSINT,
            "attributes": [
                {"type": "email", "key": "email", "value": "mark@example.com"},
            ]
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["label"], "Mark Taylor")
        self.assertEqual(response.data["source"], IdentitySource.OSINT)

    def test_merge_split_api_actions(self):
        id1 = Identity.objects.create(
            tenant_id=self.org.id,
            organization=self.org,
            label="John Doe",
            entity_type=IdentityType.PERSON,
            source=IdentitySource.MANUAL,
            owner=self.analyst,
            confidence_score=Decimal("1.000"),
        )
        id2 = Identity.objects.create(
            tenant_id=self.org.id,
            organization=self.org,
            label="Johnathan Doe",
            entity_type=IdentityType.PERSON,
            source=IdentitySource.OSINT,
            owner=self.analyst,
            confidence_score=Decimal("0.900"),
        )

        match = IdentityMatch.objects.create(
            tenant_id=self.org.id,
            candidate_a=id1,
            candidate_b=id2,
            confidence=Decimal("0.950"),
            review_status=ReviewStatus.REQUIRES_REVIEW,
            owner=self.analyst,
        )

        self.client.force_authenticate(user=self.analyst)

        # Merge
        url = reverse("identity-match-merge", args=[match.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify history
        history = IdentityMergeHistory.objects.first()
        self.assertIsNotNone(history)

        # Split
        url = reverse("identity-merge-history-split", args=[history.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
