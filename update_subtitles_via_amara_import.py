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

# Calculate the update interval depending on when the last changes were
def calculate_update_times(talk):
    talk.refresh_from_db()
    start = datetime.now(timezone.utc)
    before_update_interval = talk.amara_update_interval
    # Reload the talk from the db
    print("Before: ", before_update_interval)

    # If the talk has no subtitles it has no last changed on amara and the variable is None
    # Check such talks every 24 hours
    if talk.last_changed_on_amara == None:
        talk.amara_update_interval = timedelta(hours=24)
    # Last changes more than 180 days ago -> check every 14*24 hour
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*180):
        talk.amara_update_interval = timedelta(days=14)
    # Last changes more than 90 days ago -> check every 7*24 hour
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*90):
        talk.amara_update_interval = timedelta(days=7)
    # Last changes more than 60 days ago -> check every 24 hour
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*60):
        talk.amara_update_interval = timedelta(days=1)
    # Last changes more than 30 days ago -> check every 8 hour
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*30):
        talk.amara_update_interval = timedelta(hours=8)
    # Last changes more than 20 days ago -> check every 4 hour
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*20):
        talk.amara_update_interval = timedelta(hours=4)
    # Last changes more than 10 days ago -> check every 2 hour
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*10):
        talk.amara_update_interval = timedelta(hours=2)
    # Last changes more than 5 days ago -> check every 1 hour
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*5):
        talk.amara_update_interval = timedelta(hours=1)
    # Last changes more than 3 days ago -> check every 30 minutes
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*3):
        talk.amara_update_interval = timedelta(minutes=30)
    # Last changes more than 2 days ago -> check every 20 minutes
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*2):
        talk.amara_update_interval = timedelta(minutes=20)
    # Last changes more than 1 day ago -> check every 10 minutes
    elif talk.last_changed_on_amara <= start - timedelta(hours=24*1):
        talk.amara_update_interval = timedelta(minutes=10)
    # Last changes less than 1 day ago -> check every 5 minutes
    else:
        talk.amara_update_interval = timedelta(minutes=5)
    if talk.amara_update_interval != before_update_interval:
        print(talk.id, "before: ", before_update_interval, "after: ", talk.amara_update_interval)
        talk.save()
    else:
        print(talk.id, "same: ", before_update_interval)

start = datetime.now(timezone.utc)

print("Start: ", start)

# Check activity on talks with the next_amara_activity_check in the past:
my_talks = Talk.objects.filter(next_amara_activity_check__lte = start, unlisted = False)
print("Talks which need an activity update: ", my_talks.count())
for any in my_talks:
    any.refresh_from_db()
    # Recheck if this dataset was already
    # polled from amara
    if any.next_amara_activity_check <= start:
        any.check_activity_on_amara()
    calculate_update_times(any)

# Check the "big" amara query for talks which had a new activity
# or the flag was manually set
my_talks = Talk.objects.filter(needs_complete_amara_update = True, unlisted = False)
print("Talks which need a full amara update: ", my_talks.count())
for any in my_talks:
    any.refresh_from_db()
    # If a script runs in parallel which
    # already cleared the flag do not do
    # this again
    if any.needs_complete_amara_update:
        any.check_amara_video_data()
    calculate_update_times(any)

# Check the "big" amara query if there was no big query in the last 180d to find
# talks which have a changed complete flag without a new revision which can not
# be detected with the activity check on amara
time_delta = timedelta(seconds=0, minutes=0, hours=24*180, microseconds=0)
before_timedelta = datetime.now(timezone.utc) - time_delta
my_talks = Talk.objects.filter(amara_complete_update_last_checked__lte = before_timedelta, unlisted = False)
print("Talks which need a forced amara update: ", my_talks.count())
for any in my_talks:
    any.refresh_from_db()
    # Force is necessary, if not it won't be checked because the flag is not set
    # Make sure it has not been checked by
    # a different script during the runtime
    if any.amara_complete_update_last_checked <= before_timedelta:
        any.check_amara_video_data(force = True)
    calculate_update_times(any)

end = datetime.now(timezone.utc)
print("Start: ", start)
print("End: ", end, "      Duration: ", end - start)
