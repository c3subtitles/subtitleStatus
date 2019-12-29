# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0142_subtitle_autotiming_step'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='autotiming_step',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
