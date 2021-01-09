# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0157_add_kanboard_check_constraints'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='kanboard_private_task_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='talk',
            name='kanboard_public_task_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
