# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0058_auto_20141214_0756'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='date',
            field=models.DateTimeField(default='1970-01-01 00:00:00+01:00', blank=True),
        ),
    ]
