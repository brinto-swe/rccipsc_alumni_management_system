"""Bootstrap command for creating an initial admin user."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from users.enums import AccountStatus, UserRole


User = get_user_model()


class Command(BaseCommand):
    help = "Bootstrap the system with an initial admin user."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--username", default="system-admin")

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        username = options["username"]

        if User.objects.filter(email__iexact=email).exists():
            raise CommandError(f"A user with email {email} already exists.")

        user = User.objects.create_superuser(
            email=email,
            password=password,
            username=username,
            role=UserRole.ADMIN,
            account_status=AccountStatus.ACTIVE,
            is_active=True,
            is_verified=True,
        )
        self.stdout.write(self.style.SUCCESS(f"Bootstrapped admin user: {user.email}"))
