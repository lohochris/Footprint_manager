import pytest
from apps.organizations.models import Invitation, Organization, OrganizationMember, Workspace
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


@pytest.fixture(scope='session')
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username='testuser', email='test@example.com', password='password123')

@pytest.fixture
def auth_token(user):
    token = AccessToken.for_user(user)
    return str(token)

@pytest.fixture
def auth_client(api_client, auth_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
    return api_client

@pytest.fixture
def organization(db, user):
    org = Organization.objects.create(name='Test Org', slug='test-org', owner=user, description='A test organization')
    OrganizationMember.objects.create(organization=org, user=user, role='owner')
    return org

@pytest.fixture
def workspace(db, organization, user):
    ws = Workspace.objects.create(name='Test Workspace', slug='test-ws', organization=organization, owner=user)
    return ws

@pytest.fixture
def invitation(db, organization, user):
    token = 'dummy-token'
    invitation = Invitation.objects.create(
        organization=organization,
        email='invitee@example.com',
        token_hash=Invitation.hash_token(token),
        invited_by=user,
        status='pending',
    )
    return invitation, token
