from django.core.management.base import BaseCommand
from core.models import WorkItemMonthlyValue


class Command(BaseCommand):
    help = "Clear all actual hours"

    def handle(self, *args, **options):
        count, _ = WorkItemMonthlyValue.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {count} monthly values"
            )
        )

