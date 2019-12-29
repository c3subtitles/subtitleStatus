# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0068_auto_20150125_2227'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subtitle',
            old_name='needs_delete_from_ftp',
            new_name='needs_removal_from_ftp',
        ),
    ]
