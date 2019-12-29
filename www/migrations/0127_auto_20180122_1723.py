# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0126_auto_20171015_1701'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='has_priority',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='talk',
            name='transcript_from_trint',
            field=models.BooleanField(default=False),
        ),
    ]
