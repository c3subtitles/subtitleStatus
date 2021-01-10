# Generated by Django 2.2.17 on 2021-01-10 02:40

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0168_auto_20210109_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='blacklisted',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='event',
            name='timeslot_duration',
            field=models.TimeField(blank=True, default=datetime.time(0, 15)),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='www.Language'),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_syncing',
            field=models.TimeField(blank=True, default=datetime.time(0, 0), verbose_name=''),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_transcribing',
            field=models.TimeField(blank=True, default=datetime.time(0, 0), verbose_name=''),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_processed_translating',
            field=models.TimeField(blank=True, default=datetime.time(0, 0), verbose_name=''),
        ),
        migrations.AlterField(
            model_name='subtitle',
            name='time_quality_check_done',
            field=models.TimeField(blank=True, default=datetime.time(0, 0), verbose_name=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='blacklisted',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='talk',
            name='day',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='www.Event_Days'),
        ),
        migrations.AlterField(
            model_name='talk',
            name='duration',
            field=models.TimeField(blank=True, default=datetime.time(0, 45)),
        ),
        migrations.AlterField(
            model_name='talk',
            name='room',
            field=models.ForeignKey(default=15, on_delete=django.db.models.deletion.PROTECT, to='www.Rooms'),
        ),
        migrations.AlterField(
            model_name='talk',
            name='start',
            field=models.TimeField(blank=True, default=datetime.time(11, 0)),
        ),
        migrations.AlterField(
            model_name='talk',
            name='video_duration',
            field=models.TimeField(blank=True, default=datetime.time(0, 0)),
        ),
    ]
