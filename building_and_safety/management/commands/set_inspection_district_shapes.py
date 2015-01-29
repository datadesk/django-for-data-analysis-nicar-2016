import os
import logging
from datetime import datetime
from django.conf import settings
from django.contrib.gis.utils import LayerMapping
from lifelines import KaplanMeierFitter
from building_and_safety.models import Complaint, InspectionDistrict
from django.core.management.base import BaseCommand, CommandError
logger = logging.getLogger(__name__)


# Get the average wait time using a Kaplan-Meier Survival analysis estimate
# Make arrays of the days since complaint, and whether a case is 'closed'
# this creates the observations, and whether a "death" has been observed
def get_kmf_fit(qs):
    t = qs.values_list('days_since_complaint', flat=True)
    c = qs.values_list('is_closed', flat=True)
    kmf = KaplanMeierFitter()
    kmf.fit(t, event_observed=c)
    return kmf


# Return the mean of our KMF curve
def get_kmf_median(kmf):
    return kmf.median_


# Use our KMF fit to try and establish an average response time
# basically extracts the survival function from the curve,
# which is a pandas data frame
def get_kmf_mean(kmf):
    df = kmf.survival_function_
    df.reset_index(level=0, inplace=True)
    mean = 0
    # iterate through the rows in our data frame
    row_iterator = df.iterrows()
    last = row_iterator.next()
    for row in row_iterator:
        # convert the series objects from this and the next row to a dictionary
        n = last[1].to_dict()
        d = row[1].to_dict()
        # subtract the next value from the current, and multiply by the KM-estimate
        v = (d['timeline'] - n['timeline']) * n['KM-estimate']
        # add to our mean value
        mean += v
        # store the current row as the previous row
        last = row

    return mean


class Command(BaseCommand):
    help = "Determine the shape of inspection districts, based on complaints\
     assigned to that district overlaid with census tracts."
    data_dir = os.path.join(settings.ROOT_DIR,
                            'building_and_safety/data/inspection_districts')

    def flush_districts(self):
        logger.debug("Flushing inspection districts")
        InspectionDistrict.objects.all().delete()

    def get_number_of_complaints(self):
        for d in InspectionDistrict.objects.all():
            dist_no = d.district_number
            dist_complaints = Complaint.objects.filter(
                ladbs_inspection_district=dist_no,
                date_received__gte=datetime(2013, 7, 13)
                )
            d.complaints = dist_complaints.count()
            d.csr1_complaints = dist_complaints.filter(csr_priority="1").count()
            d.csr2_complaints = dist_complaints.filter(csr_priority="2").count()
            d.csr3_complaints = dist_complaints.filter(csr_priority="3").count()
            d.save()

    def get_wait_times(self):
        for d in InspectionDistrict.objects.all():
            qs = Complaint.objects.filter(
                ladbs_inspection_district=d,
                date_received__gte=datetime(2013, 7, 13)
                )
            csr1 = qs.filter(csr_priority="1")
            csr2 = qs.filter(csr_priority="2")
            csr3 = qs.filter(csr_priority="3")

            kmf_fit = get_kmf_fit(qs)
            kmf_fit_csr1 = get_kmf_fit(csr1)
            kmf_fit_csr2 = get_kmf_fit(csr2)
            kmf_fit_csr3 = get_kmf_fit(csr3)

            d.median_wait = get_kmf_median(kmf_fit)
            d.median_wait_csr1 = get_kmf_median(kmf_fit_csr1)
            d.median_wait_csr2 = get_kmf_median(kmf_fit_csr2)
            d.median_wait_csr3 = get_kmf_median(kmf_fit_csr3)
            d.mean_wait = get_kmf_mean(kmf_fit)

            d.save()

    def handle(self, *args, **options):
        self.flush_districts()
        logger.debug("Loading district shapes")

        shp = os.path.join(self.data_dir, 'ladbs_inspection_districts.shp')
        db2shp = {
            'polygon_4326': 'POLYGON',
            'district_number': 'ASGNAREA_G',
        }
        lm = LayerMapping(InspectionDistrict, shp, db2shp, encoding='latin-1')
        lm.save()

        logger.debug("Counting number of complaints per district")
        self.get_number_of_complaints()
        logger.debug("Calculating wait times per district")
        self.get_wait_times()
