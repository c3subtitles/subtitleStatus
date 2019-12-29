# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0141_auto_20191222_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='autotiming_step',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
