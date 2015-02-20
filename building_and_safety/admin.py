from django.contrib import admin
from building_and_safety.models import *

# Register your models here.
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('csr','full_address','date_received','date_closed','days_since_complaint','past_due_date','days_past_due_date','is_closed','more_than_one_year','lat_visited')
    list_filter = ['is_closed', 'more_than_one_year','area_planning_commission','lat_visited','investigate_further', "past_due_date"]
    search_fields = ['csr','full_address']
    fieldsets = (
        (('Derived fields'),
            {'fields':('full_address', 
                        ('is_closed', 'gt_30_days', 'gt_90_days', 'gt_180_days', 'more_than_one_year',), 
                       'days_since_complaint', 'past_due_date', 'days_past_due_date')}
        ),
        (('Raw data fields'), 
            {'fields':('csr', 'ladbs_inspection_district', 
                            ('address_house_number', 'address_house_fraction', 'address_street_direction',), 
                            ('address_street_name', 'address_street_suffix', 'address_street_suffix_direction', 'address_street_zip',), 
                            ('date_received', 'date_closed', 'date_due',), 
                            'case_flag', 'csr_priority','gis_pin', 'csr_problem_type', 'area_planning_commission', 'case_number_csr', 'response_days',
                            ('lat', 'lon',))}
        ),
        (('Notes fields'),
            {'fields':('inspector', 'inspector_phone_number',  
                        ('lat_visited', 'investigate_further', 'housing_dept_related'),
                        'notes',)}

        )

    )

admin.site.register(Complaint, ComplaintAdmin)
