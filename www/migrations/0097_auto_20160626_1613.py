# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0096_statistics_time_delta'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistics',
            name='speaker',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='subtitle',
        ),
        migrations.DeleteModel(
            name='Statistics',
        ),
    ]
