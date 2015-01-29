import os
import csv
import logging
from building_and_safety.models import InspectionDistrict
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Export a list of inspection districts and wait times."

    def handle(self, *args, **options):
        path = os.path.join(settings.ROOT_DIR, 'building_and_safety/data/inspection_district_export.csv')
        fields = ["district_number", "complaints", "csr1_complaints",
                  "csr2_complaints", "csr3_complaints", "median_wait",
                  "median_wait_csr1", "median_wait_csr2", "median_wait_csr3",
                  "mean_wait"]
        qs = InspectionDistrict.objects.all().values(*fields)

        with open(path, 'w') as csvfile:
            dw = csv.DictWriter(csvfile, fieldnames=fields)
            dw.writeheader()
            [dw.writerow(i) for i in qs]
            csvfile.close()
