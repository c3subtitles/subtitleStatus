# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0022_remove_talk_orig_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='orig_language',
            field=models.ForeignKey(to='www.Language', default=1),
            preserve_default=False,
        ),
    ]
