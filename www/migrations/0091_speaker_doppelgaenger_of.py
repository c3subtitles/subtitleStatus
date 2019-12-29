# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0090_speaker_doppelgaenger_of'),
    ]

    operations = [
        migrations.AddField(
            model_name='speaker',
            name='doppelgaenger_of',
            field=models.ForeignKey(blank=True, to='www.Speaker', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
