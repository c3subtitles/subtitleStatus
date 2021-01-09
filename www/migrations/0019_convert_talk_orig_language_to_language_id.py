# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0018_auto_20141210_0415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='orig_language',
            field=models.CharField(max_length=11, default=''),
        ),
        migrations.RunSQL(
            [
                "UPDATE www_talk AS t SET orig_language = l.id FROM www_language AS l WHERE t.orig_language = l.lang_short_2;",
                "ALTER TABLE www_talk ALTER COLUMN orig_language TYPE integer USING orig_language::integer;",
            ],
            [
                "ALTER TABLE www_talk ALTER COLUMN orig_language TYPE character varying(11) USING orig_language::character varying(11);",
                "UPDATE www_talk AS t SET orig_language = l.lang_short_2 FROM www_language AS l WHERE t.orig_language::integer = l.id;",
            ],
        ),
        migrations.AlterField(
            model_name='talk',
            name='orig_language',
            field=models.ForeignKey(to='www.Language', on_delete=models.PROTECT),
        ),
    ]
