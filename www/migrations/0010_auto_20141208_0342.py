# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0009_auto_20141208_0341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='timeslot_duration',
            field=models.TimeField(default='0:15'),
        ),
    ]
