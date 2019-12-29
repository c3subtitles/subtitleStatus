# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0006_auto_20141207_1534'),
    ]

    operations = [
        migrations.RenameField(
            model_name='links',
            old_name='link_title',
            new_name='talk_link_title',
        ),
    ]
