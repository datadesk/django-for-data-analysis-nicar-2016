from django.conf import settings
from building_and_safety.models import Complaint
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Cache the full addresses in a field on the Complaint model."

    def handle(self, *args, **options):
        for c in Complaint.objects.all():
            c.full_address = c.get_full_address()
            c.save()
