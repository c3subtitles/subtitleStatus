# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0019_convert_talk_orig_language_to_language_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtitle',
            name='language',
            field=models.CharField(max_length=15, default=''),
        ),
        migrations.RunSQL(
            [
                "UPDATE www_subtitle AS s SET language = l.id FROM www_language AS l WHERE s.language = l.lang_amara_short;",
                "ALTER TABLE www_subtitle ALTER COLUMN language TYPE integer USING language::integer;",
            ],
            [
                "ALTER TABLE www_subtitle ALTER COLUMN language TYPE character varying(15) USING language::character varying(15);",
                "UPDATE www_subtitle AS s SET language = l.lang_amara_short FROM www_language AS l WHERE s.language::integer = l.id;",
            ],
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='language',
            field=models.ForeignKey(default=1, to='www.Language', on_delete=models.PROTECT),
            preserve_default=False,
        ),
    ]
