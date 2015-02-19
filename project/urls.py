from django.conf import settings
from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.views.static import serve as static_serve
from django.views.generic import TemplateView
from building_and_safety.views import *
from django.contrib.admin.views.decorators import staff_member_required
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    # This is the URL Varnish will ping to check the server health.
    url(r'^app_status/$', 'toolbox.views.app_status', name='status'),
    url(r'^area_planning_commissions/$', AreaPlanningCommissions.as_view(), name='area-planning-commissions'),    
    url(r'^complaint/(?P<csr>[0-9]{6})/$', ComplaintDetail.as_view(), name="complaint_detail"),
    url(r'^complaint_analysis/$', ComplaintAnalysis.as_view(), name='complaint_analysis'),
    url(r'^complaint_type_breakdown/$', ComplaintTypeBreakdown.as_view(), name='complaint_type_breakdown'),
    url(r'^api/complaints.json$', open_complaints_json, name='complaints-json'),
    url(r'^api/closed_complaints.json$', closed_complaints_json, name='closed-complaints-json'),
    url(r'^api/csv/negative-date-complaints.csv', negative_date_cases_csv, name='negative-date-complaints'),
    url(r'^complaints-map/$', ComplaintsMap.as_view(), name='complaints-map'),
    url(r'^inspection_districts/$', InspectionDistricts.as_view(), name='inspection-districts'),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
        url(r'^static/(?P<path>.*)$', 'serve', {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True,
        }),
        url(r'^media/(?P<path>.*)$', 'serve', {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True,
        }),
    )

if settings.PRODUCTION:
    urlpatterns += patterns('',
        url(r'^munin/(?P<path>.*)$', staff_member_required(static_serve), {
            'document_root': settings.MUNIN_ROOT,
        })
   )
