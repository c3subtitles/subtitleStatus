#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script eliminates doppelgaenger in the visible data.
# It links everything connected to this speaker to the "highest"
# database entry of the speaker
#
# This script is meant for manual use.
# 
# Use this script if you added data in a "doppelgaenger_of_id" field of a
# speaker and want this to be applied to all the datasets belonging to the
# speaker
#
# This script fixes relations in:
# * Moves the Talk_Persons Relationship to the right speaker
# * Adds the Statistics_raw data to the right speaker
# * Adds the Statistics_Speaker data to the right speaker
#==============================================================================

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Statistics_Raw_Data, Speaker, Statistics_Speaker, Talk_Persons

# Get all Speakers with doppelgaenger_of non empty
all_doppelgaenger = Speaker.objects.all().exclude(doppelgaenger_of = None)
print(all_doppelgaenger.count())

for this_d in all_doppelgaenger:
    print("Id: " + str(this_d.id))
    # Substitute in Statistics_raw
    my_statistics_raw = Statistics_Raw_Data.objects.filter(speaker = this_d)
    my_statistics_raw.update(speaker = this_d.doppelgaenger_of)

    # Substitute in Statistics_Speaker
    my_statistics_speaker = Statistics_Speaker.objects.filter(speaker = this_d)
    my_statistics_speaker.update(speaker = this_d.doppelgaenger_of)

    # Substitute in Talk_Persons
    my_talk_persons = Talk_Persons.objects.filter(speaker = this_d)
    my_talk_persons.update(speaker = this_d.doppelgaenger_of)

print("Done!")
