import sys
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from backend.apps.organizations.models import Organization, OrganizationMember, Workspace, WorkspaceMember

User = get_user_model()

class Command(BaseCommand):
    help = "Bootstraps a development environment with a seeded administrator, organization, and workspace."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stderr.write(self.style.ERROR("ABORTED: This command can only be run in development (DEBUG=True)."))
            sys.exit(1)

        email = "admin@footprint.local"
        password = "DevPassword123!"
        org_name = "Acme Intelligence Corp"
        workspace_name = "Default Investigation Workspace"

        self.stdout.write("Initializing development environment...")

        # 1. Create Superuser
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_password(password)
            user.first_name = "Admin"
            user.last_name = "Developer"
            user.is_staff = True
            user.is_superuser = True
            user.account_status = User.Status.ACTIVE
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created dev admin user: {email}"))
        else:
            self.stdout.write(self.style.WARNING(f"User {email} already exists. Updating password."))
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.account_status = User.Status.ACTIVE
            user.save()

        # 2. Create Organization
        org, org_created = Organization.objects.get_or_create(
            slug=slugify(org_name),
            defaults={
                "name": org_name,
                "owner": user,
            }
        )
        if org_created:
            self.stdout.write(self.style.SUCCESS(f"Created organization: {org.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Organization {org.name} already exists."))

        # 3. Create Organization Membership
        org_member, om_created = OrganizationMember.objects.get_or_create(
            organization=org,
            user=user,
            defaults={
                "role": "owner"
            }
        )
        if om_created:
            self.stdout.write(self.style.SUCCESS("Assigned OWNER role for organization."))

        # 4. Create Workspace
        workspace, ws_created = Workspace.objects.get_or_create(
            organization=org,
            slug=slugify(workspace_name),
            defaults={
                "name": workspace_name,
            }
        )
        if ws_created:
            self.stdout.write(self.style.SUCCESS(f"Created workspace: {workspace.name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Workspace {workspace.name} already exists."))

        # 5. Create Workspace Membership
        ws_member, wm_created = WorkspaceMember.objects.get_or_create(
            workspace=workspace,
            user=user,
            defaults={
                "role": "owner"
            }
        )
        if wm_created:
            self.stdout.write(self.style.SUCCESS("Assigned OWNER role for workspace."))

        self.stdout.write(self.style.SUCCESS("\n=============================================="))
        self.stdout.write(self.style.SUCCESS("DEVELOPMENT ENVIRONMENT SEEDED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS("=============================================="))
        self.stdout.write(self.style.SUCCESS(f"Email:     {email}"))
        self.stdout.write(self.style.SUCCESS(f"Password:  {password}"))
        self.stdout.write(self.style.SUCCESS("==============================================\n"))
