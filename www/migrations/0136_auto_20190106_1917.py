# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0135_auto_20190106_1337'),
    ]

    operations = [
#        migrations.AddField(
#            model_name='subtitle',
#            name='autotiming_step',
#            field=models.PositiveSmallIntegerField(default=0),
#        ),
        migrations.AlterField(
            model_name='type_of',
            name='type',
            field=models.CharField(default='', max_length=50),
        ),
    ]
