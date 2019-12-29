# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0092_statistics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statistics',
            name='end',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='start',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='strokes',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='time_delta',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='words',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
