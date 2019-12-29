# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0133_auto_20180128_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='frab_id_talk',
            field=models.CharField(default='-1', max_length=10, blank=True),
        ),
    ]
