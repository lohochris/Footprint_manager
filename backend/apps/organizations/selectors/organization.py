"""Organization selectors for tenant‑isolated reads.

All selectors enforce that the requesting user is a member of the organization
or has appropriate ownership rights. They return QuerySets or model instances
without performing any write operations.
"""

import uuid
from typing import Union
from django.core.exceptions import PermissionDenied

from backend.apps.accounts.models.user import User
from ..models import Organization, OrganizationMember


def get_user_organization_membership(user: User, organization_id) -> OrganizationMember:
    """Return the membership object for *user* in the given organization.

    Raises ``PermissionDenied`` if the user is not a member.
    """
    try:
        return OrganizationMember.objects.select_related("organization").get(
            user=user, organization_id=organization_id
        )
    except OrganizationMember.DoesNotExist:
        raise PermissionDenied("User is not a member of this organization.")


def get_organization_by_id(user: User, org_id: uuid.UUID | str) -> Organization:
    """Retrieve an organization ensuring tenant isolation.

    The caller must be a member of the organization; otherwise ``PermissionDenied``
    is raised.
    """
    # Verify membership first (adds a tiny DB hit but guarantees security).
    get_user_organization_membership(user, org_id)
    return Organization.objects.get(pk=org_id)


def list_organizations_for_user(user: User):
    """Return a ``QuerySet`` of all organizations the user belongs to.
    """
    return Organization.objects.filter(members__user=user).distinct()


def is_user_owner(user: User, organization: Organization) -> bool:
    """True if *user* is the recorded owner of *organization*.
    """
    return organization.owner.id == user.id
