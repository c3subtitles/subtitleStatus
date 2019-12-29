# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0134_auto_20180510_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='frab_id_prefix',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
# already done by hand
#        migrations.AddField(
#            model_name='subtitle',
#            name='autotiming_step',
#            field=models.PositiveSmallIntegerField(default=0),
#        ),
        migrations.AlterField(
            model_name='speaker',
            name='frab_id',
            field=models.CharField(blank=True, default='-1', max_length=12),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='is_original_lang',
            field=models.BooleanField(default=False, verbose_name='original language'),
        ),
        migrations.AlterField(
            model_name='talk',
            name='frab_id_talk',
            field=models.CharField(blank=True, default='-1', max_length=12),
        ),
    ]
