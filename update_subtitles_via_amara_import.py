#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script checks for every talk with an amara key if there were any
# "activities" since the last check
# If there was an activity it triggers the "big" amara update
#
# If a talk didn't have a big amara update during the last 24h it forces also
# a big update for this talk to avoid missing a complete flag which can
# unfortunately be set without a change of revision which means the talk has
# no activity in the activity check
#
# This script is meant to be run as a cronjob
#==============================================================================

import os
from datetime import datetime, timezone, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()

from www.models import Talk

start = datetime.now(timezone.utc)

print("Start: ", start)

# Check activity on talks with the next_amara_activity_check in the past:
my_talks = Talk.objects.filter(next_amara_activity_check__lte = start, blacklisted = False)
print("Talks which need an activity update: ", my_talks.count())
for any in my_talks:
    any.check_activity_on_amara()

# Check the "big" amara query for talks which had a new activity
my_talks = Talk.objects.filter(needs_complete_amara_update = True, blacklisted = False)
print("Talks which need a full amara update: ", my_talks.count())
for any in my_talks:
    any.check_amara_video_data()

# Check the "big" amara query if there was no big query in the last 24h to find
# talks which have a changed complete flag without a new revision which can not
# be detected with the activity check on amara
time_delta = timedelta(seconds = 0, minutes = 0, hours = 24, microseconds = 0)
before_24h = datetime.now(timezone.utc) - time_delta
my_talks = Talk.objects.filter(amara_complete_update_last_checked__lte = before_24h, blacklisted = False)
print("Talks which need a forced amara update: ", my_talks.count())
for any in my_talks:
    # Force is necessary, if not it won't be checked because the flag is not set
    any.check_amara_video_data(force = True)

end = datetime.now(timezone.utc)
print("Start: ", start)
print("End: ", end, "      Duration: ", end - start)
