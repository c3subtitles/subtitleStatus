#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script changes the update intervals for talks for the amara sync
#
# Use this especially if a new event is in the database and older events
# need less often updates
#
#==============================================================================

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Event
from datetime import datetime

update_intervals = {}

# 0 30c3
update_intervals[0] = "03:00:00"

# 1  31c3
update_intervals[1] = "03:00:00"

# 3 Unbekanntes Event - Testevent
update_intervals[3] = "00:00:10"

# 4 32c3
update_intervals[4] = "03:00:00"

# 5 33c3
update_intervals[5] = "03:00:00"

# 6 34c3
update_intervals[6] = "02:00:00"

# 7 eh18
update_intervals[7] = "03:00:00"

# 8 35c3
update_intervals[8] = "00:00:15"

# 9 35c3-chaoswest
update_intervals[9] = "01:00:00"

# 10 35c3-wikipaka
update_intervals[10] = "01:00:00"

# 11 36c3
update_intervals[11] = "00:00:15"

# 12 36c3-chaoswest
update_intervals[12] = "01:00:00"

# 13 36c3-wikipaka
update_intervals[13] = "01:00:00"

# 14 WikidataCon 2019
update_intervals[14] = "01:00:00"

# 15 Hidden Service - Ein Digital Verteiltes Online-Chaos
update_intervals[15] = "01:00:00"

# 16 rC3
update_intervals[16] = "00:00:10"

# 17 rC3 - hacc
update_intervals[17] = "00:00:10"

# 18 rC3 - wikipaka
update_intervals[18] = "00:00:10"

for any_event_id in update_intervals:
    my_event = Event.objects.get(id = any_event_id)
    my_talks = Talk.objects.filter(event = my_event)
    my_talks.update(amara_update_interval = update_intervals[any_event_id])
