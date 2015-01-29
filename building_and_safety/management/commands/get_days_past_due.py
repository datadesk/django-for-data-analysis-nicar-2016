from datetime import datetime
from django.conf import settings
from building_and_safety.models import Complaint
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Find the number of days past a complaint's due date before it was closed, if applicable."

    def handle(self, *args, **options):
        most_recent_date = datetime.strptime("7/13/2014", "%m/%d/%Y").date()

        for c in Complaint.objects.exclude(date_due=None):
            if c.date_closed:
                t = c.date_closed - c.date_due
            else:
                t = most_recent_date - c.date_due

            if t.days > 0:
                c.past_due_date = True
                c.days_past_due_date = t.days

                c.save()