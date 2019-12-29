# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0050_auto_20141210_0927'),
    ]

    operations = [
        migrations.RenameField(
            model_name='links',
            old_name='talk_link_title',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='links',
            old_name='talk_link_url',
            new_name='url',
        ),
    ]
