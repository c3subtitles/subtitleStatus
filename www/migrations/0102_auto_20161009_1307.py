# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0101_auto_20161009_1255'),
    ]

    operations = [
        migrations.RenameModel('Statistics','Statistics_raw')
    ]
