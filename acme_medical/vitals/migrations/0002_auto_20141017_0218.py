# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

from vitals.models import Vital

import os
import yaml

def addVitalMetadata(apps, schema_editor):
   filename = os.path.join(settings.FIXTURES_DIR, 'initial_data.yaml')
   f = file(filename)
   vitals = yaml.load(f)
   f.close()
   for vital in vitals:
      v = Vital(**vital)
      v.save()

class Migration(migrations.Migration):

    dependencies = [
        ('vitals', '0001_initial'),
    ]



    operations = [
         migrations.RunPython(addVitalMetadata)
    ]
