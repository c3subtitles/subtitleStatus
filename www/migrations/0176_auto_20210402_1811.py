# Generated by Django 2.2.17 on 2021-04-02 18:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0175_auto_20210402_1807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='amara_update_interval',
            field=models.DurationField(blank=True, default=datetime.timedelta(seconds=600)),
        ),
    ]
