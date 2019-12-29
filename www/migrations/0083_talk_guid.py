# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0082_subtitle_last_changed_on_amara'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='guid',
            field=models.CharField(blank=True, default='', max_length=40),
            preserve_default=True,
        ),
    ]
