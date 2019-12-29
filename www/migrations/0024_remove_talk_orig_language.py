# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0023_talk_orig_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='talk',
            name='orig_language',
        ),
    ]
