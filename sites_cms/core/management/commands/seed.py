from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load sample content for local development."

    def handle(self, *args, **options):
        # Each feature adds its own sample content here, in the same pull
        # request as its models. Running this twice must be safe.
        self.stdout.write("Nothing to seed yet.")
