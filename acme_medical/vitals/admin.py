from django.contrib import admin
from vitals.models import Patient
from vitals.models import Vital
from vitals.models import Measurement

admin.site.register([Patient, Vital, Measurement])
