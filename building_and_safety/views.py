import json
import csv
import calculate
import collections
from datetime import datetime
from django.db.models import Count, Avg
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


# Create your views here.
class ComplaintAnalysis(TemplateView):
    template_name = "complaint_analysis.html"

    def get_context_data(self, **kwargs):
        # Let's only grab complaints that are filed more than a year ago
        open_cases = Complaint.objects.filter(is_closed=False)
        closed_cases = Complaint.objects.filter(is_closed=True)

        # overall complaints not addressed within a year
        over_one_year = Complaint.gt_one_year.filter(more_than_one_year=True)
        open_over_one_year = over_one_year.filter(is_closed=False)
        closed_over_one_year = over_one_year.filter(is_closed=True)

        total_count = Complaint.objects.all().count()
        total_csr1 = Complaint.objects.filter(csr_priority="1").count()
        total_csr2 = Complaint.objects.filter(csr_priority="2").count()
        total_csr3 = Complaint.objects.filter(csr_priority="3").count()

        open_cases_count = open_cases.count()
        open_cases_csr1 = open_cases.filter(csr_priority="1").count()
        open_cases_csr2 = open_cases.filter(csr_priority="2").count()
        open_cases_csr3 = open_cases.filter(csr_priority="3").count()

        closed_cases_count = closed_cases.count()
        closed_cases_csr1 = closed_cases.filter(csr_priority="1").count()
        closed_cases_csr2 = closed_cases.filter(csr_priority="2").count()
        closed_cases_csr3 = closed_cases.filter(csr_priority="3").count()

        over_one_year_count = over_one_year.count()
        over_one_year_csr1 = over_one_year.filter(csr_priority="1").count()
        over_one_year_csr2 = over_one_year.filter(csr_priority="2").count()
        over_one_year_csr3 = over_one_year.filter(csr_priority="3").count()

        open_over_one_year_count = open_over_one_year.count()
        open_over_one_year_csr1 = open_over_one_year.filter(csr_priority="1").count()
        open_over_one_year_csr2 = open_over_one_year.filter(csr_priority="2").count()
        open_over_one_year_csr3 = open_over_one_year.filter(csr_priority="3").count()

        closed_over_one_year_count = closed_over_one_year.count()
        closed_over_one_year_csr1 = closed_over_one_year.filter(csr_priority="1").count()
        closed_over_one_year_csr2 = closed_over_one_year.filter(csr_priority="2").count()
        closed_over_one_year_csr3 = closed_over_one_year.filter(csr_priority="3").count()

        avg_wait_time = Complaint.objects.filter(is_closed=True, days_since_complaint__gte=0)\
            .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']
        avg_wait_time_csr1 = Complaint.objects.filter(is_closed=True, days_since_complaint__gte=0, csr_priority="1")\
            .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']        
        avg_wait_time_csr2 = Complaint.objects.filter(is_closed=True, days_since_complaint__gte=0, csr_priority="2")\
            .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']        
        avg_wait_time_csr3 = Complaint.objects.filter(is_closed=True, days_since_complaint__gte=0, csr_priority="3")\
            .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']        

        all_complaints = Complaint.objects.exclude(days_since_complaint__lt=0)
        kmf_fit = get_kmf_fit(all_complaints)
        median_wait_time_kmf = get_kmf_median(kmf_fit)
        mean_wait_time_kmf = get_kmf_mean(kmf_fit)

        csr1 = all_complaints.filter(csr_priority="1")
        kmf_fit_csr1 = get_kmf_fit(csr1)
        median_wait_time_csr1_kmf = get_kmf_median(kmf_fit_csr1)
        mean_wait_time_csr1_kmf = get_kmf_mean(kmf_fit_csr1)

        csr2 = all_complaints.filter(csr_priority="2")
        kmf_fit_csr2 = get_kmf_fit(csr2)   
        median_wait_time_csr2_kmf = get_kmf_median(kmf_fit_csr2)
        mean_wait_time_csr2_kmf = get_kmf_mean(kmf_fit_csr2)

        csr3 = all_complaints.filter(csr_priority="3")
        kmf_fit_csr3 = get_kmf_fit(csr3)
        median_wait_time_csr3_kmf = get_kmf_median(kmf_fit_csr3)
        mean_wait_time_csr3_kmf = get_kmf_mean(kmf_fit_csr3)

        region_names = ['Central','East Los Angeles','Harbor','North Valley','South Los Angeles','South Valley','West Los Angeles']
        regions = {}

        complaints_2011 = Complaint.objects.filter(date_received__year=2011)
        complaints_2012 = Complaint.objects.filter(date_received__year=2012)
        complaints_2013 = Complaint.objects.filter(date_received__year=2013)
        complaints_2014 = Complaint.objects.filter(date_received__year=2014)

        complaints_2011_kmf_fit = get_kmf_fit(complaints_2011)
        complaints_2012_kmf_fit = get_kmf_fit(complaints_2012)
        complaints_2013_kmf_fit = get_kmf_fit(complaints_2013)
        complaints_2014_kmf_fit = get_kmf_fit(complaints_2014)

        complaints_2011_median_wait_time = get_kmf_median(complaints_2011_kmf_fit)
        complaints_2012_median_wait_time = get_kmf_median(complaints_2012_kmf_fit)
        complaints_2013_median_wait_time = get_kmf_median(complaints_2013_kmf_fit)
        complaints_2014_median_wait_time = get_kmf_median(complaints_2014_kmf_fit)

        eastside_complaints_2011 = complaints_2011.filter(area_planning_commission="East Los Angeles")
        eastside_complaints_2012 = complaints_2012.filter(area_planning_commission="East Los Angeles")
        eastside_complaints_2013 = complaints_2013.filter(area_planning_commission="East Los Angeles")
        eastside_complaints_2014 = complaints_2014.filter(area_planning_commission="East Los Angeles")

        eastside_complaints_2011_kmf_fit = get_kmf_fit(eastside_complaints_2011)
        eastside_complaints_2012_kmf_fit = get_kmf_fit(eastside_complaints_2012)
        eastside_complaints_2013_kmf_fit = get_kmf_fit(eastside_complaints_2013)
        eastside_complaints_2014_kmf_fit = get_kmf_fit(eastside_complaints_2014)

        eastside_complaints_2011_median_wait_time = get_kmf_median(eastside_complaints_2011_kmf_fit)
        eastside_complaints_2012_median_wait_time = get_kmf_median(eastside_complaints_2012_kmf_fit)
        eastside_complaints_2013_median_wait_time = get_kmf_median(eastside_complaints_2013_kmf_fit)
        eastside_complaints_2014_median_wait_time = get_kmf_median(eastside_complaints_2014_kmf_fit)

        csr_1_complaints_2013 = complaints_2013.filter(csr_priority="1")
        csr_1_complaints_2013_kmf = get_kmf_fit(csr_1_complaints_2013)
        csr_1_complaints_2013_median_wait = get_kmf_median(csr_1_complaints_2013_kmf)


        for region in region_names:
            qs = Complaint.objects.filter(area_planning_commission=region, days_since_complaint__gte=0)
            regions[region] = {}
            regions[region]['total'] = qs.count()
            regions[region]['gt_30_days'] = qs.filter(gt_30_days=True).count()
            regions[region]['gt_90_days'] = qs.filter(gt_90_days=True).count()
            regions[region]['gt_180_days'] = qs.filter(gt_180_days=True).count()
            regions[region]['gt_year'] = qs.filter(more_than_one_year=True).count()

            # want to grab average time to resolve for all complaints
            # not just those older than a year
            regions[region]['avg_days_to_resolve'] = Complaint.objects.filter(area_planning_commission=region,is_closed=True, days_since_complaint__gte=0)\
                .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']
            regions[region]['avg_days_csr1'] = Complaint.objects\
                .filter(area_planning_commission=region,is_closed=True, csr_priority="1", days_since_complaint__gte=0)\
                .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']
            regions[region]['avg_days_csr2'] = Complaint.objects\
                .filter(area_planning_commission=region,is_closed=True, csr_priority="2", days_since_complaint__gte=0)\
                .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']
            regions[region]['avg_days_csr3'] = Complaint.objects\
                .filter(area_planning_commission=region,is_closed=True, csr_priority="3", days_since_complaint__gte=0)\
                .aggregate(Avg('days_since_complaint'))['days_since_complaint__avg']
            regions[region]['avg_complaints_per_year'] = get_avg_complaints_filed_per_year(region)

            region_csr1 = qs.filter(csr_priority="1")
            region_csr2 = qs.filter(csr_priority="2")
            region_csr3 = qs.filter(csr_priority="3")

            regional_kmf_fit = get_kmf_fit(qs)
            regional_kmf_fit_csr1 = get_kmf_fit(region_csr1)
            regional_kmf_fit_csr2 = get_kmf_fit(region_csr2)
            regional_kmf_fit_csr3 = get_kmf_fit(region_csr3)

            regions[region]['median_wait_kmf'] = get_kmf_median(regional_kmf_fit)
            regions[region]['median_wait_kmf_csr1'] = get_kmf_median(regional_kmf_fit_csr1)
            regions[region]['median_wait_kmf_csr2'] = get_kmf_median(regional_kmf_fit_csr2)
            regions[region]['median_wait_kmf_csr3'] = get_kmf_median(regional_kmf_fit_csr3)

            regions[region]['mean_wait_kmf'] = get_kmf_mean(regional_kmf_fit)
            regions[region]['mean_wait_kmf_csr1'] = get_kmf_mean(regional_kmf_fit_csr1)
            regions[region]['mean_wait_kmf_csr2'] = get_kmf_mean(regional_kmf_fit_csr2)
            regions[region]['mean_wait_kmf_csr3'] = get_kmf_mean(regional_kmf_fit_csr3)

            regions[region]['per_gt_30_days'] = calculate.percentage(regions[region]['gt_30_days'],regions[region]['total'])
            regions[region]['per_gt_90_days'] = calculate.percentage(regions[region]['gt_90_days'],regions[region]['total'])
            regions[region]['per_gt_180_days'] = calculate.percentage(regions[region]['gt_180_days'],regions[region]['total'])
            regions[region]['per_gt_year'] = calculate.percentage(regions[region]['gt_year'],regions[region]['total'])

            regions[region]['csr1'] = region_csr1.count()
            regions[region]['csr2'] = region_csr2.count()
            regions[region]['csr3'] = region_csr3.count()

            regions[region]['csr1_percent'] = calculate.percentage(region_csr1.count(), regions[region]['total'])
            regions[region]['csr2_percent'] = calculate.percentage(region_csr2.count(), regions[region]['total'])
            regions[region]['csr3_percent'] = calculate.percentage(region_csr3.count(), regions[region]['total'])

        return locals()


class ComplaintTypeBreakdown(TemplateView):
    template_name = "complaint_type_breakdown.html"

    def get_context_data(self, **kwargs):
        region_names = ['Central', 'East Los Angeles', 'Harbor', 'North Valley', 'South Los Angeles', 'South Valley', 'West Los Angeles']
        regions = {}

        for region in region_names:
            qs = Complaint.objects.filter(area_planning_commission=region, days_since_complaint__gte=0)
            regions[region] = {}

            types = Complaint.objects.filter(area_planning_commission=region)\
                .values('csr_problem_type').annotate(count=Count('csr_problem_type')).order_by('-count')[0:10]

            regions[region]['types'] = types

        return locals()


class ComplaintsMap(TemplateView):
    template_name = 'complaints_map.html'

    def get_context_data(self, **kwargs):
        context = super(ComplaintsMap, self).get_context_data(**kwargs)
        return context


class ComplaintDetail(DetailView):
    template_name = "complaint_detail.html"
    model = Complaint
    slug_field = "csr"
    slug_url_kwarg = "csr"

    def get_context_data(self, **kwargs):
        context = super(ComplaintDetail, self).get_context_data(**kwargs)
        return context


class VisitedComplaints(ListView):
    template_name = "visited_complaints.html"
    model = Complaint
    queryset = Complaint.objects.filter(lat_visited=True)


class InspectionDistricts(TemplateView):
    """
    Render a template showing the number of open and closed cases for each 
    LADBS inspection district
    """
    template_name = "inspection_districts.html"

    def get_context_data(self, **kwargs):
        context = super(InspectionDistricts, self).get_context_data(**kwargs)
        districts = Complaint.objects.order_by('ladbs_inspection_district')\
                    .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district')
        district_dict = collections.OrderedDict()

        for d in districts:
            district = {}
            district_complaints = Complaint.objects.filter(days_since_complaint__gte=0,ladbs_inspection_district=d)
            district["open"] = district_complaints.filter(is_closed=False).count()
            district["closed"] = district_complaints.filter(is_closed=True).count() 
            district["2011"] = district_complaints.filter(date_received__year=2011).count()
            district["2012"] = district_complaints.filter(date_received__year=2012).count()
            district["2013"] = district_complaints.filter(date_received__year=2013).count()
            district["2014"] = district_complaints.filter(date_received__year=2014).count()
            district["by_due"] = district_complaints.filter(past_due_date=True).count()
            district["total"] = district["open"] + district["closed"]
            district["percent_open"] = calculate.percentage(district["open"], district["total"])
            district["percent_past_due"] = calculate.percentage(district["by_due"], district["total"])
            district["region"] = ' / '.join(district_complaints.order_by('area_planning_commission')\
                .values_list('area_planning_commission', flat=True).distinct('area_planning_commission'))
            district_dict[d] = district

        return locals()


class AreaPlanningCommissions(TemplateView):
    """
    Render a template showing the number of open and closed cases for each 
    Area Planning Comission
    """
    template_name = "area_planning_commissions.html"

    def get_context_data(self, **kwargs):
        regions = ["East Los Angeles","Central","South Los Angeles","Harbor","North Valley","South Valley","West Los Angeles"]
        apc_dict = collections.OrderedDict()

        all_complaints = Complaint.objects.filter(days_since_complaint__gte=0)
        all_complaints_2011 = all_complaints.filter(date_received__year=2011)
        all_complaints_2012 = all_complaints.filter(date_received__year=2012)
        all_complaints_2013 = all_complaints.filter(date_received__year=2013)
        all_complaints_2014 = all_complaints.filter(date_received__year=2014)

        all_complaints_total = all_complaints.count()
        all_complaints_past_due = all_complaints.filter(past_due_date=True).count()
        all_complaints_percent_past_due = calculate.percentage(all_complaints_past_due, all_complaints_total)
        all_complaints_districts = all_complaints.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
        all_complaints_per_inspector = all_complaints_total / all_complaints_districts

        all_complaints_2011_total = all_complaints_2011.count()
        all_complaints_2011_past_due = all_complaints_2011.filter(past_due_date=True).count()
        all_complaints_2011_percent_past_due = calculate.percentage(all_complaints_2011_past_due, all_complaints_2011_total)
        all_complaints_2011_districts = all_complaints_2011.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
        all_complaints_2011_per_inspector = all_complaints_2011_total / all_complaints_2011_districts

        all_complaints_2012_total = all_complaints_2012.count()
        all_complaints_2012_past_due = all_complaints_2012.filter(past_due_date=True).count()
        all_complaints_2012_percent_past_due = calculate.percentage(all_complaints_2012_past_due, all_complaints_2012_total)
        all_complaints_2012_districts = all_complaints_2012.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
        all_complaints_2012_per_inspector = all_complaints_2012_total / all_complaints_2012_districts

        all_complaints_2013_total = all_complaints_2013.count()
        all_complaints_2013_past_due = all_complaints_2013.filter(past_due_date=True).count()
        all_complaints_2013_percent_past_due = calculate.percentage(all_complaints_2013_past_due, all_complaints_2013_total)
        all_complaints_2013_districts = all_complaints_2013.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
        all_complaints_2013_per_inspector = all_complaints_2013_total / all_complaints_2013_districts

        all_complaints_2014_total = all_complaints_2014.count()
        all_complaints_2014_past_due = all_complaints_2014.filter(past_due_date=True).count()
        all_complaints_2014_percent_past_due = calculate.percentage(all_complaints_2014_past_due, all_complaints_2014_total)
        all_complaints_2014_districts = all_complaints_2014.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
        all_complaints_2014_per_inspector = all_complaints_2014_total / all_complaints_2014_districts

        for r in regions:
            region = {}
            region_complaints = Complaint.objects.filter(days_since_complaint__gte=0,area_planning_commission=r)
            region_complaints_2011 = region_complaints.filter(date_received__year=2011)
            region_complaints_2012 = region_complaints.filter(date_received__year=2012)
            region_complaints_2013 = region_complaints.filter(date_received__year=2013)
            region_complaints_2014 = region_complaints.filter(date_received__year=2014)

            districts_count = region_complaints.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
            districts_count_2011 = region_complaints_2011.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
            districts_count_2012 = region_complaints_2012.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
            districts_count_2013 = region_complaints_2013.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()
            districts_count_2014 = region_complaints_2014.order_by('ladbs_inspection_district')\
                .values_list('ladbs_inspection_district', flat=True).distinct('ladbs_inspection_district').count()

            region["total_complaints"] = region_complaints.count()
            region["past_due"] = region_complaints.filter(past_due_date=True).count()
            region["percent_past_due"] = calculate.percentage(region["past_due"], region["total_complaints"])
            region["districts"] = districts_count
            region["complaints_per_inspector"] = region["total_complaints"] / districts_count

            region["2011_total"] = region_complaints_2011.count()
            region["2011_past_due"] = region_complaints_2011.filter(past_due_date=True).count()
            region["2011_percent_past_due"] = calculate.percentage(region["2011_past_due"], region["2011_total"])
            region["2011_districts"] = districts_count_2011
            region["2011_complaints_per_inspector"] = region["2011_total"] / districts_count_2011

            region["2012_total"] = region_complaints_2012.count()
            region["2012_past_due"] = region_complaints_2012.filter(past_due_date=True).count()
            region["2012_percent_past_due"] = calculate.percentage(region["2012_past_due"], region["2012_total"])
            region["2012_districts"] = districts_count_2012
            region["2012_complaints_per_inspector"] = region["2012_total"] / districts_count_2012

            region["2013_total"] = region_complaints_2013.count()
            region["2013_past_due"] = region_complaints_2013.filter(past_due_date=True).count()
            region["2013_percent_past_due"] = calculate.percentage(region["2013_past_due"], region["2013_total"])
            region["2013_districts"] = districts_count_2013
            region["2013_complaints_per_inspector"] = region["2013_total"] / districts_count_2013

            region["2014_total"] = region_complaints_2014.count()
            region["2014_past_due"] = region_complaints_2014.filter(past_due_date=True).count()
            region["2014_percent_past_due"] = calculate.percentage(region["2014_past_due"], region["2014_total"])
            region["2014_districts"] = districts_count_2014
            region["2014_complaints_per_inspector"] = region["2014_total"] / districts_count_2014

            apc_dict[r] = region 

        return locals()


def negative_date_cases_csv(request):
    """
    Get cases that were closed before they were opened in the database
    Send these to DBS so they can figure out what's wrong with them.
    """
    qs = Complaint.objects.defer('more_than_one_year','gt_30_days','gt_90_days','gt_180_days','days_since_complaint','neighborhoodv6','full_address').filter(days_since_complaint__lt=0)
    return djqscsv.render_to_csv_response(qs)


def open_complaints_json(request):
    """
    Pull all the open complaints that were open for more than a year.
    """
    complaints = Complaint.gt_one_year\
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

