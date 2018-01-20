#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# Forces the Statistics Data in Statistics_Raw_Data and Talk to be new calculated
# 
#
#==============================================================================

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()

#from django.db.models import Q
from www.models import Statistics_Raw_Data, Talk

# Statistics_Raw_Data
my_statistics = Statistics_Raw_Data.objects.filter()
for any_statistics in my_statistics:
    any_statistics.recalculate(True)

# Whole Talk Statistics
my_statistics = Talk.objects.filter()
for any_statistics in my_statistics:
    any_statistics.recalculate(True)

"""    
# Talk, only Speakers Time Statistics
my_statistics = Talk.objects.filter(recalculate_speakers_statistics = True)
for any_statistics in my_statistics:
    any_statistics.recalculate_speakers_in_talk_statistics()

# Create the entries for Statistics_Event if necessary, ignore #3
all_events = Event.objects.all().exclude(id = 3)
for any in all_events:
    any.create_statistics_event_entries()

# Event Statistics
my_statistics = Statistics_Event.objects.filter(recalculate_statistics = True)
for any_statistics in my_statistics:
    any_statistics.recalculate()

# Talk_Persons
my_statistics = Talk_Persons.objects.filter(recalculate_statistics = True)
for any_statistics in my_statistics:
    any_statistics.recalculate()

# Statistics Speakers
my_statistics = Statistics_Speaker.objects.filter(recalculate_statistics = True)
for any_statistics in my_statistics:
    any_statistics.recalculate()    
"""
print("Done!")

