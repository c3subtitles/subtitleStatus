#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script fixes wrong data from the schedules import like 
# language = None in some cases
#
# Use this script after a fahrplan import with a fahrplan which has wrong data
# in some fields
#==============================================================================

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Links, Tracks, Type_of, Speaker, Event, Event_Days, Rooms, Language, Subtitle, States

#==============================================================================
# 30c3
#==============================================================================
# talk id 30 and 86 are imported as language = none (id 0) should be english (id 287)
ids = [30, 86]
for this_id in ids:
    my_talk = Talk.objects.get(id = this_id)
    if my_talk.orig_language_id != 287:
        my_talk.orig_language_id = 287
        my_talk.save()

# the event title is not the long version
my_event = Event.objects.get(id = 0)
if my_event.title != "30. Chaos Communication Congress":
    my_event.title = "30. Chaos Communication Congress"
    my_event.save()
        
#==============================================================================
# 31c3
#==============================================================================
# nothing so far?


#==============================================================================
# 32c3
#==============================================================================
# talk id 602 and 603 are imported as language = none (id 0) should be english (id 287)
ids = [602, 603]
for this_id in ids:
    my_talk = Talk.objects.get(id = this_id)
    if my_talk.orig_language_id != 287:
        my_talk.orig_language_id = 287
        my_talk.save()