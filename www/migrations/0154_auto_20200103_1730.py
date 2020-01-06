# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0153_auto_20200102_1837'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='lang_code_media',
            field=models.CharField(default='', blank=True, max_length=4),
        ),
    ]
