# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0136_auto_20190106_1917'),
    ]

    operations = [
#        migrations.AddField(
#            model_name='subtitle',
#            name='autotiming_step',
#            field=models.PositiveSmallIntegerField(default=0),
#        ),
        migrations.AlterField(
            model_name='speaker',
            name='frab_id',
            field=models.CharField(max_length=20, default='-1', blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='frab_id_talk',
            field=models.CharField(max_length=20, default='-1', blank=True),
        ),
    ]
