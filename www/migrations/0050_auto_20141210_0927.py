# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0049_auto_20141210_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='subtitle_talk',
            field=models.CharField(max_length=300, blank=True, default=' '),
        ),
    ]
