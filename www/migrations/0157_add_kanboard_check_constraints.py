# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0156_add_kanboard_fields'),
    ]

    operations = [
        migrations.RunSQL(
            [
                "ALTER TABLE www_event ADD CONSTRAINT www_event_kanboard_public_xor_private_project_id CHECK ((kanboard_public_project_id IS NULL) = (kanboard_private_project_id IS NULL))",
                "ALTER TABLE www_subtitle ADD CONSTRAINT www_subtitle_kanboard_public_xor_private_task_id CHECK ((kanboard_public_task_id IS NULL) = (kanboard_private_task_id IS NULL))",
            ],
            [
                "ALTER TABLE www_event DROP CONSTRAINT www_event_kanboard_public_xor_private_project_id",
                "ALTER TABLE www_subtitle DROP CONSTRAINT www_subtitle_kanboard_public_xor_private_task_id",
            ],
        ),
    ]
