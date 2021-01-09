# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0167_auto_20210109_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='trint_folder_id',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AddField(
            model_name='talk',
            name='trint_transcript_id',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
    ]
