# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0047_auto_20141210_0922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='subtitle_talk',
            field=models.CharField(default=' ', blank=True, max_length=200),
        ),
    ]
