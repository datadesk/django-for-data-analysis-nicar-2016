import json
import csv
import calculate
import collections
from datetime import datetime
from django.db.models import Count
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, TemplateView
from building_and_safety.models import Complaint

from lifelines import KaplanMeierFitter


def get_avg_complaints_filed_per_year(region):
    qs = Complaint.objects.filter(area_planning_commission=region, days_since_complaint__gte=0)\
            .extra(select={'year':"date_part('year',date_received)"}).values('year')\
            .annotate(count=Count('id')).order_by('year')
    total = 0

    for year in qs:
        total += year['count']

    # now we find the average for the four years
    # July 13 is the 194th day of the year, so divide by 3 + 194.0 / 365.0,
    avg = total / 3.5315
    return avg


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


def get_counts_by_csr(qs):
    counts = {}
    counts["csr1"] = qs.filter(csr_priority="1").count()
    counts["csr2"] = qs.filter(csr_priority="2").count()
    counts["csr3"] = qs.filter(csr_priority="3").count()
    return counts


class ComplaintAnalysis(TemplateView):
    # The HTML template we're going to use, found in the /templates directory
    template_name = "complaint_analysis.html"

    def get_context_data(self, **kwargs):
        # Quick notation to access all complaints
        complaints = Complaint.objects.all()

        # Quick means of accessing both open and closed cases
        open_cases = complaints.filter(is_closed=False)
        closed_cases = complaints.filter(is_closed=True)

        # Overall complaints not addressed within a year
        over_one_year = complaints.filter(more_than_one_year=True)
        open_over_one_year = over_one_year.filter(is_closed=False)
        closed_over_one_year = over_one_year.filter(is_closed=True)

        # Total counts of cases, all priority levels
        total_count = complaints.all().count()
        total_by_csr = get_counts_by_csr(complaints)

        # Counts of open cases, all priority levels
        open_cases_count = open_cases.count()
        open_by_csr = get_counts_by_csr(open_cases)

        # Counts of cases that have been open fore more than a year, all priority levels
        open_over_one_year_count = open_over_one_year.count()
        open_over_one_year_by_csr = get_counts_by_csr(open_over_one_year)

        # Counts of cases that were closed, but have been open for more than a year, all priority levels.
        closed_over_one_year_count = closed_over_one_year.count()
        closed_over_one_year_by_csr = get_counts_by_csr(closed_over_one_year)

        # A much better means of getting expected wait times is to use a survival analysis function
        # In this case, we use a Kaplan-Meier estimator from the Python package lifelines
        # We repeat this for all complaints, and for each CSR priority levels.
        all_complaints = Complaint.objects.exclude(days_since_complaint__lt=0)
        kmf_fit = get_kmf_fit(all_complaints)
        median_wait_time_kmf = get_kmf_median(kmf_fit)

        csr1 = all_complaints.filter(csr_priority="1")
        kmf_fit_csr1 = get_kmf_fit(csr1)
        median_wait_time_csr1_kmf = get_kmf_median(kmf_fit_csr1)

        csr2 = all_complaints.filter(csr_priority="2")
        kmf_fit_csr2 = get_kmf_fit(csr2)   
        median_wait_time_csr2_kmf = get_kmf_median(kmf_fit_csr2)

        csr3 = all_complaints.filter(csr_priority="3")
        kmf_fit_csr3 = get_kmf_fit(csr3)
        median_wait_time_csr3_kmf = get_kmf_median(kmf_fit_csr3)

        region_names = ['Central','East Los Angeles','Harbor','North Valley','South Los Angeles','South Valley','West Los Angeles']
        regions = {}

        # Iterate over each name in our region_names list
        for region in region_names:
            # Filter for complaints in each region
            qs = complaints.filter(area_planning_commission=region, days_since_complaint__gte=0)
            # create a data dictionary for the region
            regions[region] = {}
            # get a count of how many complaints total are in the queryset
            regions[region]['total'] = qs.count()
            regions[region]['avg_complaints_per_year'] = get_avg_complaints_filed_per_year(region)

            # Separate the complaints into querysets of their respective priority levels 
            region_csr1 = qs.filter(csr_priority="1")
            region_csr2 = qs.filter(csr_priority="2")
            region_csr3 = qs.filter(csr_priority="3")

            # Find the KMF fit for all complaints in the area and by each priority level
            regional_kmf_fit = get_kmf_fit(qs)
            regional_kmf_fit_csr1 = get_kmf_fit(region_csr1)
            regional_kmf_fit_csr2 = get_kmf_fit(region_csr2)
            regional_kmf_fit_csr3 = get_kmf_fit(region_csr3)

            # Get the median value from the KMF fit. 
            regions[region]['median_wait_kmf'] = get_kmf_median(regional_kmf_fit)
            regions[region]['median_wait_kmf_csr1'] = get_kmf_median(regional_kmf_fit_csr1)
            regions[region]['median_wait_kmf_csr2'] = get_kmf_median(regional_kmf_fit_csr2)
            regions[region]['median_wait_kmf_csr3'] = get_kmf_median(regional_kmf_fit_csr3)

            regions[region]['gt_year'] = qs.filter(more_than_one_year=True).count()

        return locals()


class ComplaintTypeBreakdown(TemplateView):
    """
    Break down complaints by the type received in each Area Planning Commission.
    """
    template_name = "complaint_type_breakdown.html"

    def get_context_data(self, **kwargs):
        region_names = ['Central', 'East Los Angeles', 'Harbor', 'North Valley', 'South Los Angeles', 'South Valley', 'West Los Angeles']
        regions = {}

        for region in region_names:
            qs = Complaint.objects.filter(area_planning_commission=region, days_since_complaint__gte=0)
            regions[region] = {}

            # Grab the top 10 types of complaints in each area 
            # (There are way too many to list all of them) 
            types = Complaint.objects.filter(area_planning_commission=region)\
                .values('csr_problem_type').annotate(count=Count('csr_problem_type')).order_by('-count')[0:10]

            regions[region]['types'] = types

        return locals()


class ComplaintsMap(TemplateView):
    """
    A map we use to display open and closed complaints older than one year in a Leaflet-based template.
    In the HTML template, we pull in both the open_complaints_json and closed_complaints_json views.
    """
    template_name = 'complaints_map.html'

    def get_context_data(self, **kwargs):
        context = super(ComplaintsMap, self).get_context_data(**kwargs)
        return context


class ComplaintDetail(DetailView):
    """
    Detail field with additional information about each complaint.
    """
    template_name = "complaint_detail.html"
    model = Complaint
    slug_field = "csr"
    slug_url_kwarg = "csr"

    def get_context_data(self, **kwargs):
        context = super(ComplaintDetail, self).get_context_data(**kwargs)
        return context


def open_complaints_json(request):
    """
    Pull all the open complaints that were open for more than a year.
    """
    complaints = Complaint.objects\
        .filter(is_closed=False, more_than_one_year=True).exclude(lat=None, lon=None)

    complaints = list(complaints)
    features = [complaint.as_geojson_dict() for complaint in complaints]
    objects = {
        'type': "FeatureCollection",
        'features': features
    }

    response = json.dumps(objects)
    return HttpResponse(response, content_type='text/json')


def closed_complaints_json(request):
    """
    Pull all the closed complaints that were open for more than a year.
    """
    complaints = Complaint.objects\
        .filter(is_closed=True, more_than_one_year=True).exclude(lat=None, lon=None)

    complaints = list(complaints)
    features = [complaint.as_geojson_dict() for complaint in complaints]
    objects = {
        'type': "FeatureCollection",
        'features': features
    }

    response = json.dumps(objects)
    return HttpResponse(response, content_type='text/json')

