from django.core.management.base import BaseCommand

from accounts.models import Permission, Role
from accounts.rbac import create_default_roles


class Command(BaseCommand):
    help = "Initialize RBAC permissions and roles"

    def handle(self, *args, **options):
        perm_codes = [code for code, _ in Permission.CODE_CHOICES]
        for code in perm_codes:
            Permission.objects.get_or_create(code=code)
        created_perms_count = Permission.objects.filter(code__in=perm_codes).count()
        self.stdout.write(f"Created {created_perms_count} permissions")

        roles = create_default_roles()
        self.stdout.write(self.style.SUCCESS(f"Created roles: {', '.join(r.name for r in roles.values())}"))