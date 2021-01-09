# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import www.models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0158_auto_20201225_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='comment',
            field=models.TextField(blank=True, null=True, default=''),
        ),
        migrations.AlterField(
            model_name='event',
            name='schedule_xml_link',
            field=www.models.MaybeURLField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='speaker_json_link',
            field=www.models.MaybeURLField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='link_to_writable_pad',
            field=www.models.MaybeURLField(blank=True, default=''),
        ),
    ]
