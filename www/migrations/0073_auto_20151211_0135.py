# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0072_auto_20150126_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event_days',
            name='date',
            field=models.DateField(blank=True, default='1970-01-01'),
        ),
        migrations.AlterField(
            model_name='event_days',
            name='day_end',
            field=models.DateTimeField(blank=True, default='1970-01-01 00:00'),
        ),
        migrations.AlterField(
            model_name='event_days',
            name='day_start',
            field=models.DateTimeField(blank=True, default='1970-01-01 00:00'),
        ),
    ]
