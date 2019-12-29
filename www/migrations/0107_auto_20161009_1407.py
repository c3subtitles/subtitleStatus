# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0106_auto_20161009_1359'),
    ]

    operations = [
        migrations.RenameModel("Statistics_raw","Statistics_Raw_Data")
    ]
