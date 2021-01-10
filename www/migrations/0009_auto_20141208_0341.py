# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import make_aware
from datetime import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0008_auto_20141207_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateField(default=make_aware(datetime.min)),
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateField(default=make_aware(datetime.min)),
        ),
    ]
