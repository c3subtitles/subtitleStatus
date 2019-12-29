# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0137_auto_20190106_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='hashtag',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
    ]
