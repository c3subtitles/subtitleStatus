# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0148_auto_20200102_1749'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='talk',
            name='link_to_logo',
        ),
    ]
