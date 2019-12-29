# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0105_statistics_event_statistics_speaker'),
    ]

    operations = [
        migrations.RenameModel("Statistics_raw","Statistics_Raw_Data")
    ]
