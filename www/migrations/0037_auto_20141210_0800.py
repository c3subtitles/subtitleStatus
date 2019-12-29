# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0036_auto_20141210_0756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='days',
            field=models.PositiveSmallIntegerField(blank=True, default=1),
        ),
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateField(blank=True, default='1970-01-01'),
        ),
        migrations.AlterField(
            model_name='event',
            name='schedule_version',
            field=models.CharField(max_length=50, default='0.0', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateField(blank=True, default='1970-01-01'),
        ),
        migrations.AlterField(
            model_name='event',
            name='timeslot_duration',
            field=models.TimeField(blank=True, default='00:15'),
        ),
        migrations.AlterField(
            model_name='event_days',
            name='date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='event_days',
            name='day_end',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='event_days',
            name='day_start',
            field=models.DateTimeField(blank=True),
        ),
    ]
