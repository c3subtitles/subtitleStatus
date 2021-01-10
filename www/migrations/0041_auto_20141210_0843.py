# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import make_aware
from datetime import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0040_auto_20141210_0843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='date',
            field=models.DateTimeField(blank=True, default=make_aware(datetime.min)),
        ),
    ]
