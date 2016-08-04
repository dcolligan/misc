from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from vitals import views

urlpatterns = patterns('',
   url(r'^$', views.home),

   # CRUD urls
   url(r'^patients/?$', views.PatientList.as_view()),
   url(r'^patients/(?P<pk>[0-9]+)/$', views.PatientDetail.as_view()),
   url(r'^vitals/?$', views.VitalList.as_view()),
   url(r'^vitals/(?P<pk>[0-9]+)$', views.VitalDetail.as_view()),
   url(r'^measurements/?$', views.MeasurementList.as_view()),
   url(r'^measurements/(?P<pk>[0-9]+)$', views.MeasurementDetail.as_view()),

   # Page urls
   url(r'^pages/patientDetail/(?P<patient_id>[0-9]+)$', views.PagePatientDetail.as_view()),
   url(r'^pages/vitalDetail/(?P<patient_id>[0-9]+)/(?P<vital_slug>[A-Za-z-]+)$', views.PageVitalDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
