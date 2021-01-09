# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0164_auto_20210108_1833'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='talk',
            name='youtube_key',
        ),
    ]
