# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0128_transcript'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='transcript_by',
            field=models.ForeignKey(to='www.Transcript', default=0, on_delete=models.SET_DEFAULT),
        ),
    ]
