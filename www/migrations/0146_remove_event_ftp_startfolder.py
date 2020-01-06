# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0145_talk_internal_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='ftp_startfolder',
        ),
    ]
