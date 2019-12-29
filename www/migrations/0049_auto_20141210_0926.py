# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0048_auto_20141210_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='subtitle_talk',
            field=models.CharField(blank=True, default=' ', max_length=500),
        ),
    ]
