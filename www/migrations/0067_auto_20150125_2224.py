# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0066_auto_20150118_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_syncing',
            field=models.TimeField(blank=True, default='00:00', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_transcribing',
            field=models.TimeField(blank=True, default='00:00', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_translating',
            field=models.TimeField(blank=True, default='00:00', verbose_name=''),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_quality_check_done',
            field=models.TimeField(blank=True, default='00:00', verbose_name=''),
        ),
    ]
