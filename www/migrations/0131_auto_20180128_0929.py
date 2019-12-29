# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0130_auto_20180128_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcript',
            name='creator',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
