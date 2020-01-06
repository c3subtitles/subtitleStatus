# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0149_remove_talk_link_to_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='talk',
            name='link_to_readable_pad',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='pad_id',
        ),
    ]
