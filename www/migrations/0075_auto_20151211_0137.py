# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0074_auto_20151211_0136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event_days',
            name='date',
            field=models.DateField(default='1970-02-01', blank=True),
        ),
    ]
