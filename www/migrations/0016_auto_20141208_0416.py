# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0015_auto_20141208_0412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_syncing',
            field=models.TimeField(default='00:00'),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_transcribing',
            field=models.TimeField(default='00:00'),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_translating',
            field=models.TimeField(default='00:00'),
        ),
    ]
