# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0086_talk_file_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='talk',
            old_name='file_name',
            new_name='filename',
        ),
    ]
