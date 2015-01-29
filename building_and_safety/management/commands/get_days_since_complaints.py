from datetime import datetime
from django.conf import settings
from building_and_safety.models import Complaint
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Find the number of days since a complaint was filed, and when any action was taken, if it was."

    def handle(self, *args, **options):
        most_recent_date = datetime.strptime("7/13/2014", "%m/%d/%Y").date()

        for c in Complaint.objects.all():
            if c.date_closed:
                t = c.date_closed - c.date_received
            else:
                t = most_recent_date - c.date_received

            c.days_since_complaint = t.days
            
            if c.days_since_complaint > 365:
                c.more_than_one_year = True
            else:
                c.more_than_one_year = False
            
            if c.days_since_complaint > 180:
                c.gt_180_days = True

            if c.days_since_complaint > 90:
                c.gt_90_days = True

            if c.days_since_complaint > 30:
                c.gt_30_days = True

            c.save()