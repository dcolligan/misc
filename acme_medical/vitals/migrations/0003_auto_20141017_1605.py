# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from vitals.models import Measurement
from vitals.models import Patient
from vitals.models import Vital

import random
import datetime
from django.utils import timezone

def addSeedData(apps, schema_editor):
   vitals = Vital.objects.all()
   num_measurements = 20
   patient_names = ['Joe Bob', 'Jill Jane', 'Bill John']
   now = timezone.now()

   for patient_name in patient_names:
      patient = Patient(**{'name' : patient_name})
      patient.save()

      for vital in vitals:

         for i in range(num_measurements):
            date = now - datetime.timedelta(hours = i)
            args = {
                  'vital': vital,
                  'patient' : patient,
                  'date': date,
                  'value1' : random.randint(0, 100),
                  'value2' : random.randint(0, 100),
            }
            m = Measurement(**args)
            m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('vitals', '0002_auto_20141017_0218'),
    ]

    operations = [
         migrations.RunPython(addSeedData)
    ]
