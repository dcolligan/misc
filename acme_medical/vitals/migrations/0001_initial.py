# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value1', models.DecimalField(max_digits=10, decimal_places=5)),
                ('value2', models.DecimalField(max_digits=10, decimal_places=5)),
                ('date', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vital',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('slug', models.TextField()),
                ('unitLabel', models.TextField()),
                ('unitLabelShort', models.TextField()),
                ('unitCount', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='measurement',
            name='patient',
            field=models.ForeignKey(to='vitals.Patient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='measurement',
            name='vital',
            field=models.ForeignKey(to='vitals.Vital'),
            preserve_default=True,
        ),
    ]
