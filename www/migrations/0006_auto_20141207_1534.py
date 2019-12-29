# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0005_auto_20141207_0235'),
    ]

    operations = [
        migrations.RenameField(
            model_name='links',
            old_name='title',
            new_name='link_title',
        ),
        migrations.RenameField(
            model_name='links',
            old_name='url',
            new_name='talk_link_url',
        ),
    ]
