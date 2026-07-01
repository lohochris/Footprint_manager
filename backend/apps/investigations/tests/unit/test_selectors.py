import pytest
from django.contrib.auth import get_user_model

from backend.apps.investigations.models.investigation import Investigation
from backend.apps.investigations.selectors.investigation_selector import InvestigationSelector
from backend.apps.organizations.models import Organization, Workspace


@pytest.fixture
def org(db):
    return Organization.objects.create(name='Test Org')

@pytest.fixture
def workspace(db, org):
    return Workspace.objects.create(name='Test Workspace', organization=org)

@pytest.fixture
def investigations(db, org, workspace):
    invs = []
    for i in range(5):
        inv = Investigation.objects.create(
            case_number=f"CASE-{i}",
            title=f"Investigation {i}",
            organization=org,
            workspace=workspace,
            owner=get_user_model().objects.create(username=f'user{i}'),
            status='draft',
            priority='medium'
        )
        invs.append(inv)
    return invs

def test_list_returns_paginated(org, investigations):
    items, meta = InvestigationSelector.list(org, page=1, page_size=2)
    assert len(items) == 2
    assert meta['total_items'] == 5
    assert meta['total_pages'] == 3

def test_filter_by_status(org, investigations):
    # change status of one investigation
    inv = investigations[0]
    inv.status = 'open'
    inv.save()
    items, meta = InvestigationSelector.list(org, filters={'status': ['open']})
    assert len(items) == 1
    assert items[0].pk == inv.pk
