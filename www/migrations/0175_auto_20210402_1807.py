# Generated by Django 2.2.17 on 2021-04-02 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0174_auto_20210402_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='amara_update_interval',
            field=models.DurationField(blank=True, default='0001-01-01T00:10:00+00:00'),
        ),
    ]
