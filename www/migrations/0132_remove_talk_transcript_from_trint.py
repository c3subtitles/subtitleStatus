# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0131_auto_20180128_0929'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='talk',
            name='transcript_from_trint',
        ),
    ]
