from django.contrib.gis import admin
from building_and_safety.models import *
from django.contrib.gis.admin import OSMGeoAdmin

# Register your models here.
class ComplaintAdmin(OSMGeoAdmin):
    list_display = ('csr','full_address','date_received','date_closed','days_since_complaint','past_due_date','days_past_due_date','is_closed','more_than_one_year','lat_visited')
    list_filter = ['is_closed', 'more_than_one_year','area_planning_commission','lat_visited','investigate_further', "past_due_date"]
    search_fields = ['csr','full_address']

admin.site.register(Complaint, ComplaintAdmin)
