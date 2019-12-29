# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0038_auto_20141210_0812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='amara_order',
            field=models.PositiveSmallIntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='language',
            name='lang_short_2',
            field=models.CharField(max_length=3, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='language',
            name='lang_short_srt',
            field=models.CharField(max_length=15, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='language',
            name='language_de',
            field=models.CharField(max_length=40, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='language',
            name='language_native',
            field=models.CharField(max_length=40, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='state',
            field=models.ForeignKey(blank=True, to='www.States'),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_syncing',
            field=models.TimeField(blank=True, default='00:00'),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_transcribing',
            field=models.TimeField(blank=True, default='00:00'),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_translating',
            field=models.TimeField(blank=True, default='00:00'),
        ),
    ]
