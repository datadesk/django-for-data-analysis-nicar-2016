import calculate
from datetime import datetime
from django.conf import settings
from django.db.models import Count
from building_and_safety.models import Complaint
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Spit out a sanity check of complaint due dates."

    def handle(self, *args, **options):
        days_to_due_list = []

        for c in Complaint.objects.exclude(date_due=None):
            days_to_due = c.date_due - c.date_received
            days_to_due_list.append(days_to_due.days)

        # print out a quick sanity check
        calculate.summary_stats(days_to_due_list)

        # also print a frequency count
        counts = dict(zip(days_to_due_list,map(days_to_due_list.count, days_to_due_list)))
        print counts