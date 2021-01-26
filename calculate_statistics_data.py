#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts does the calculations in all the statistic modules and in other
# models like the Talk_Persons module and the Talk-Module
# 
# It is meant to be run as cronjob
#
# It filters all datasets with a recalculation-needed flag set and lets
# them execute the calculations
# 
# 
#==============================================================================

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()

#from django.db.models import Q
from www.models import Statistics_Raw_Data, Talk, Talk_Persons, Statistics_Speaker, Statistics_Event, Event

# Statistics_Raw_Data
my_statistics = Statistics_Raw_Data.objects.filter(recalculate_statistics = True)
for any_statistics in my_statistics:
    any_statistics.refresh_from_db()
    any_statistics.recalculate()

# Whole Talk Statistics
my_statistics = Talk.objects.filter(recalculate_talk_statistics = True)
for any_statistics in my_statistics:
    any_statistics.refresh_from_db()
    any_statistics.recalculate_whole_talk_statistics()

# Talk, only Speakers Time Statistics
my_statistics = Talk.objects.filter(recalculate_speakers_statistics = True)
for any_statistics in my_statistics:
    any_statistics.refresh_from_db()
    any_statistics.recalculate_speakers_in_talk_statistics()

# Create the entries for Statistics_Event if necessary, ignore #3
all_events = Event.objects.all().exclude(id = 3)
for any in all_events:
    any.refresh_from_db()
    any.create_statistics_event_entries()

# Event Statistics
my_statistics = Statistics_Event.objects.filter(recalculate_statistics = True)
for any_statistics in my_statistics:
    any_statistics.refresh_from_db()
    any_statistics.recalculate()

# Talk_Persons
my_statistics = Talk_Persons.objects.filter(recalculate_statistics = True)
for any_statistics in my_statistics:
    any_statistics.refresh_from_db()
    any_statistics.recalculate()

# Statistics Speakers
my_statistics = Statistics_Speaker.objects.filter(recalculate_statistics = True)
for any_statistics in my_statistics:
    any_statistics.refresh_from_db()
    any_statistics.recalculate()

print("Done!")

