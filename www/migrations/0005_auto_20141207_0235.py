# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0004_auto_20141207_0207'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subtitle',
            name='comment',
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_syncing',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_transcribing',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_translating',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='talk',
            name='video_duration',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='talk',
            name='youtube_key',
            field=models.CharField(max_length=20),
        ),
    ]
