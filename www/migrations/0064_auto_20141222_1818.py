# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0063_subtitle_time_quality_check_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='needs_automatic_syncing',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='talk',
            name='event',
            field=models.ForeignKey(blank=True, to='www.Event', default=3, on_delete=models.SET_DEFAULT),
        ),
        migrations.AlterField(
            model_name='talk',
            name='type_of',
            field=models.ForeignKey(blank=True, to='www.Type_of', default=9, on_delete=models.SET_DEFAULT),
        ),
    ]
