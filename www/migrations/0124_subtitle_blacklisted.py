# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0123_event_cdn_subtitles_root_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='blacklisted',
            field=models.BooleanField(default=False),
        ),
    ]
