# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0031_auto_20141210_0615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subtitle',
            name='language',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='orig_language',
        ),
    ]
