# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0140_auto_20191222_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='links',
            name='url',
            field=models.URLField(blank=True, max_length=300),
        ),
    ]
