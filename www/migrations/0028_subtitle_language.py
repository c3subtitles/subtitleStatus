# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0027_remove_subtitle_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='language',
            field=models.ForeignKey(default=1, to='www.Language'),
            preserve_default=False,
        ),
    ]
