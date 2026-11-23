from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

USERNAME = "admin"
PASSWORD = "admin"
EMAIL = "admin@example.com"


class Command(BaseCommand):
    help = "Create the local admin user (admin / admin). Local use only."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "Refusing to create a known-password admin when DEBUG is off."
            )
        User = get_user_model()
        if User.objects.filter(username=USERNAME).exists():
            self.stdout.write("Local admin already exists.")
            return
        User.objects.create_superuser(USERNAME, EMAIL, PASSWORD)
        self.stdout.write(f"Created local admin: {USERNAME} / {PASSWORD}")
