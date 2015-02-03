import json
import logging
import managers
import calculate
from datetime import datetime
from django.db.models import Avg
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, Polygon, MultiPolygon
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
    A list of complaints filed to the L.A. department of Building and Safety
    """
    csr = models.IntegerField(db_index=True)
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
    csr_priority = models.CharField(max_length=1, blank=True, null=True)
    gis_pin = models.CharField(max_length=20, blank=True, null=True)
    csr_problem_type = models.CharField(max_length=255, blank=True, null=True)
    area_planning_commission = models.CharField(max_length=20, blank=True, null=True)
    case_number_csr = models.CharField(max_length=255, blank=True, null=True)
    response_days = models.CharField(max_length=4, null=True, blank=True, help_text="Since open and closed cases calculate this differently, it's useless.")
    # lat_long = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(null=True)
    lon = models.FloatField(null=True)

    # Add-ons
    point_4326 = models.PointField(srid=4326, null=True, blank=True, verbose_name="Complaint Location")
    is_closed = models.BooleanField()
    more_than_one_year = models.BooleanField(default=False)
    gt_30_days = models.BooleanField(default=False)
    gt_90_days = models.BooleanField(default=False)
    gt_180_days = models.BooleanField(default=False)
    days_since_complaint = models.IntegerField(null=True, verbose_name="Days since complaint was filed",
        help_text="Days since the complaint was filed or days since filed until it was addressed.")
    past_due_date = models.BooleanField(default=False)
    days_past_due_date = models.IntegerField(null=True)
    neighborhoodv6 = models.ForeignKey('NeighborhoodV6', null=True, blank=True,
        help_text='Neighborhood the complaint occurred in.')
    full_address = models.CharField(max_length=255, blank=True, null=True)
    inspector = models.CharField(max_length=255, blank=True, null=True)
    inspector_phone_number = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)
    lat_visited = models.BooleanField(default=False, verbose_name="Has been visited by an LAT reporter")
    investigate_further = models.BooleanField(default=False)
    housing_dept_related = models.BooleanField(default=False)

    # Managers
    objects = models.GeoManager()
    gt_one_year = managers.OlderThanOneYearManager()

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

    def as_geojson_dict(self):
        as_dict = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(self.point_4326.x),
                    float(self.point_4326.y)
                ]
            },
            "properties": {
                "d": dateformat.format(self.date_received, 'F j, Y'),
                "c": self.get_closed_date(),
                "t": self.csr_problem_type,
                "p": self.csr_priority
            }
        }
        return as_dict


class NeighborhoodV6(models.Model):
    """
    The sixth version of Los Angeles Times neighborhoods
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    has_statistics = models.BooleanField('Stats', default=True)
    population = models.FloatField(null=True, blank=True)
    population_source = models.CharField(max_length=50)
    population_source_explainer = models.TextField()
    NEIGHBORHOOD_TYPE_CHOICES = (
        ('standalone-city', 'Standalone city'),
        ('segment-of-a-city', 'Segment of a city'),
        ('unincorporated-area', 'Unincorporated'),
        ('unclassified', 'Unclassified')
    )
    type = models.CharField(max_length=300, choices=NEIGHBORHOOD_TYPE_CHOICES,
                            default='unclassified')
    COUNTY_CHOICES = (
        ('los-angeles', 'Los Angeles'),
        ('orange', 'Orange'),
    )
    county = models.CharField(max_length=300, choices=COUNTY_CHOICES)
    square_miles = models.FloatField(null=True, blank=True)
    square_feet = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    # Boundaries
    GEOM_FIELD_LIST = (
        # We can use this list later in views to exclude
        # bulky geometry fields from database queries
        'polygon_4326', 'simple_polygon_4326',
    )
    polygon_4326 = models.MultiPolygonField(srid=4326, null=True, blank=True)
    simple_polygon_4326 = models.MultiPolygonField(srid=4326, null=True, blank=True)

    # Add-ons
    total_complaints = models.IntegerField(default=0)
    open_complaints = models.IntegerField(default=0)
    closed_complaints = models.IntegerField(default=0)
    open_over_one_year = models.IntegerField(default=0)
    closed_over_one_year = models.IntegerField(default=0)
    total_unresolved_after_one_year = models.IntegerField(default=0)
    percent_over_one_year_to_response = models.FloatField(null=True)
    avg_days_to_response = models.FloatField(null=True)
    kmf_median_days_to_response = models.FloatField(null=True)

    # Managers
    objects = models.GeoManager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Neighborhood (V6)'
        verbose_name_plural = 'Neighborhoods (V6)'

    def __unicode__(self):
        return unicode(self.name)

    def set_complaint_objects(self):
        Complaint.objects.filter(point_4326__intersects=self.polygon_4326)\
            .update(neighborhoodv6=self)

    def get_total_complaints(self):
        return self.complaint_set.count()

    def get_open_complaints(self):
        return self.complaint_set.filter(is_closed=False).count()

    def get_closed_complaints(self):
        return self.complaint_set.filter(is_closed=True).count()

    def get_open_over_one_year(self):
        return self.complaint_set.filter(is_closed=False, more_than_one_year=True).count()

    def get_closed_over_one_year(self):
        return self.complaint_set.filter(is_closed=True, more_than_one_year=True).count()

    def get_total_unresolved_after_one_year(self):
        return self.open_over_one_year + self.closed_over_one_year

    def get_percent_over_one_year_to_response(self):
        qs = self.complaint_set.filter(date_received__lte=datetime(2013, 7, 13))
        return calculate.percentage(qs.filter(more_than_one_year=True).count(), qs.count())

    def get_avg_days_to_response(self):
        return self.complaint_set.filter(is_closed=True)\
            .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']

    def get_kmf_median_days_to_response(self):
        qs = self.complaint_set.all()
        if qs.count() > 0:
            kmf_fit = get_kmf_fit(qs)
            return get_kmf_median(kmf_fit)

    def as_geojson(self):
        as_dict = {
            "type": "Feature",
            "geometry":  self.get_polygon(),
            "properties": {
                "name": self.name,
                "med": self.kmf_median_days_to_response
            }
        }
        return as_dict

    def get_polygon(self):
        return json.loads(self.polygon_4326.json)

    def get_square_miles(self):
        """
        Returns the area in square miles
        """
        if not self.polygon_4326:
            return False

        # Reproject the polygon from 4326, which is measured in
        # decimal degrees to 3310,  NAD83 California State Planes, Zone V,
        # which is measured in feet.
        copy = self.polygon_4326.transform(2229, clone=True)

        # One square foot equals 0.0929 square meters,
        # so we can do the conversion like so
        # square_feet = square_meters / 0.0929
        square_feet = copy.area

        # There are 27,878,400 square feet in a square mile,
        # so we can do the conversion like so
        square_miles = square_feet / 27878400.0
        return square_miles

    def get_simple_polygon(self, tolerance=200):
        """
        Simplifies the source polygon so it doesn't use so many points.

        Provide a tolerance score the indicates how sharply the
        the lines should be redrawn.

        Returns the new geometry in WKT format
        """
        # fetch the source polygon
        source = self.polygon_4326

        # Transform the source out of lng/lat before the simplification
        copy = source.transform(900913, clone=True)

        # simplify the source
        simple = copy.simplify(tolerance, True)

        # Transform the new poly back to its SRID
        simple.transform(4326)

        # if the result is a polygon...
        if simple.geom_type == 'Polygon':
            # stuff it in a new MultiPolygon
            simple = MultiPolygon(simple)

        # return the WKT of the result
        return simple.wkt


class InspectionDistrict(models.Model):
    district_number = models.CharField(max_length=4, blank=True, null=True)
    polygon_4326 = models.MultiPolygonField(srid=4326, null=True, blank=True)
    # number of complaints in that district from July 13, 2013 - July 12 2014
    complaints = models.IntegerField(blank=True, null=True)
    csr1_complaints = models.IntegerField(blank=True, null=True)
    csr2_complaints = models.IntegerField(blank=True, null=True)
    csr3_complaints = models.IntegerField(blank=True, null=True)
    # calculate the mean number of days for a complaint to be addressed
    median_wait = models.FloatField(blank=True, null=True)
    median_wait_csr1 = models.FloatField(blank=True, null=True)
    median_wait_csr2 = models.FloatField(blank=True, null=True)
    median_wait_csr3 = models.FloatField(blank=True, null=True)
    mean_wait = models.FloatField(blank=True, null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return unicode(self.district_number)

    def save(self, *args, **kwargs):
        # if geom ends up as a polygon, make it a MultiPolygon
        if self.polygon_4326 and isinstance(self.polygon_4326, Polygon):
            self.polygon_4326 = MultiPolygon(self.polygon_4326)

        super(InspectionDistrict, self).save(*args, **kwargs)

    def get_polygon(self):
        return json.loads(self.polygon_4326.json)

    def as_geojson(self):
        as_dict = {
            "type": "Feature",
            "geometry":  self.get_polygon(),
            "properties": {
                "dist": self.district_number,
                "num_complaints": self.complaints,
                "mean_wait": self.mean_wait,
                "median_wait": self.median_wait
            }
        }
        return as_dict
