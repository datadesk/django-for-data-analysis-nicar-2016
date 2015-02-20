import json
import logging
import calculate
from datetime import datetime
from django.db import models
from django.db.models import Avg
from django.utils import dateformat

from lifelines import KaplanMeierFitter

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

def get_kmf_median(kmf):
    return kmf.median_

class Complaint(models.Model):
    """
    A list of complaints filed to the L.A. Department of Building and Safety
    """
    csr = models.IntegerField(db_index=True, help_text='Customer Service Record number')
    ladbs_inspection_district = models.CharField(max_length=4, blank=True, null=True)
    address_house_number = models.CharField(max_length=10, blank=True, null=True)
    address_house_fraction = models.CharField(max_length=10, blank=True, null=True)
    address_street_direction = models.CharField(max_length=1, blank=True, null=True)
    address_street_name = models.CharField(max_length=255, blank=True, null=True)
    address_street_suffix = models.CharField(max_length=10, blank=True, null=True)
    address_street_suffix_direction = models.CharField(max_length=1, blank=True, null=True)
    address_street_zip = models.CharField(max_length=10,null=True, blank=True)
    date_received = models.DateField(blank=True, null=True)
    date_closed = models.DateField(blank=True, null=True)
    date_due = models.DateField(blank=True, null=True)
    case_flag = models.BooleanField()
    csr_priority = models.CharField(max_length=1, blank=True, null=True, help_text='Priority level, 1 is the most severe, 3 is a quality of life nuisance.')
    gis_pin = models.CharField(max_length=20, blank=True, null=True, help_text='Parcel identification number')
    csr_problem_type = models.CharField(max_length=255, blank=True, null=True)
    area_planning_commission = models.CharField(max_length=20, blank=True, null=True)
    case_number_csr = models.CharField(max_length=255, blank=True, null=True)
    response_days = models.CharField(max_length=4, null=True, blank=True, help_text="Since open and closed cases calculate this differently, it's useless.")
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)

    # Add-ons
    full_address = models.CharField(max_length=255, blank=True, null=True)
    is_closed = models.BooleanField()
    gt_30_days = models.BooleanField(default=False, verbose_name="Older than 30 days")
    gt_90_days = models.BooleanField(default=False, verbose_name="Older than 90 days")
    gt_180_days = models.BooleanField(default=False, verbose_name="Older than 180 days")
    more_than_one_year = models.BooleanField(default=False, verbose_name="Older than one year")
    days_since_complaint = models.IntegerField(null=True, verbose_name="Days since complaint was filed",
        help_text="Days since the complaint was filed or days since filed until it was addressed.")
    past_due_date = models.BooleanField(default=False)
    days_past_due_date = models.IntegerField(null=True)

    # Fields to fill out manually
    inspector = models.CharField(max_length=255, blank=True, null=True)
    inspector_phone_number = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)
    lat_visited = models.BooleanField(default=False, verbose_name="Whether a location has been visited by an LAT reporter")
    investigate_further = models.BooleanField(default=False)
    housing_dept_related = models.BooleanField(default=False, verbose_name="Many complaints actually fall under the jurisdiction of the housing department.")

    # Managers
    objects = models.Manager()

    class Meta:
        ordering = ("-date_received",)

    def __unicode__(self):
        return unicode(self.csr)

    def get_full_address(self):
        address_components = [self.address_house_number, self.address_house_fraction, self.address_street_direction,
            self.address_street_name, self.address_street_suffix, self.address_street_suffix_direction]
        full_address = [component for component in address_components if component != ' ']
        return ' '.join(full_address)

    def get_closed_date(self):
        if self.date_closed:
            return dateformat.format(self.date_closed,'F j, Y')
        else:
            return None

    def get_related_complaints(self):
        qs = Complaint.objects.filter(full_address=self.full_address).exclude(csr=self.csr)
        return qs

    def get_days_since_complaint(self):
        """
        Calculate the days since a complaint was filed and when it was addressed.
        If a complaint is still unaddressed, use the date the data was pulled from the DB. 
        """
        most_recent_date = datetime.strptime("7/13/2014", "%m/%d/%Y").date()
        if self.date_closed:
            t = self.date_closed - self.date_received
        else:
            t = most_recent_date - self.date_received

        return t.days

    def get_gt_t_days(self, n):
        if self.days_since_complaint > n:
            return True
        return False

    def get_days_past_due(self):
        most_recent_date = datetime.strptime("7/13/2014", "%m/%d/%Y").date()
        if self.date_closed:
            t = self.date_closed - self.date_due
        else:
            t = most_recent_date - self.date_due

        if t.days > 0:
            return True, t.days
        else:
            return False, 0

    def as_geojson_dict(self):
        """
        Method to return each feature in the DB as a geojson object.
        """
        as_dict = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(self.lon),
                    float(self.lat)
                ]
            },
            "properties": {
                "address": self.full_address,
                "csr": self.csr,
                "date": dateformat.format(self.date_received, 'F j, Y'),
                "closed": self.get_closed_date(),
                "type": self.csr_problem_type,
                "priority": self.csr_priority
            }
        }
        return as_dict
