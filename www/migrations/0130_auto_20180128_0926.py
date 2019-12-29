# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0129_talk_transcript_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcript',
            name='creator',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
