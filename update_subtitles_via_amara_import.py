#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script checks for every talk with an amara key if there were any
# "activities" since the last check
# If there was an activity it triggerts the "big" amara update
#
# If a talk didn't have a big amara update during the last 24h it forces also
# a big update for this talk to avoid missing a complete flag which can
# unfortunately be set without a change of revision which means the talk has
# no acitivity in the activity check
#
# This script is meant to be run as a cronjob
#==============================================================================

import os
from datetime import datetime, timezone, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Language, Subtitle, States, Statistics_Raw_Data

import credentials as cred


# Function to completely reset an subtitle
# Used if a subtitle was formerly set to complete but isn't anymore
def reset_subtitle(my_subtitle):
    # Stuff which needs to be done in any case, no matter if its a translation or not
    my_subtitle.complete = False
    my_subtitle.needs_removal_from_ftp = True
    my_subtitle.needs_removal_from_YT = True
    my_subtitle.last_changed_on_amara = datetime.now(timezone.utc)

    # If the subtitle is the original language,reset all states to the start
    if my_subtitle.is_original_lang:
        my_subtitle.time_processed_transcribing = "00:00:00"
        my_subtitle.time_processed_syncing = "00:00:00"
        my_subtitle.time_quality_check_done = "00:00:00"
        my_subtitle.state_id = 2 # Transcribed until
        # Reset all related statistics to None to recalculate them
        # In the Talk model
        my_talk = Talk.objects.get(id = my_subtitle.talk.id)
        my_talk.recalculate_talk_statistics = True
        my_talk.recalculate_speakers_statistics = True
        my_talk.save()
        # In the Statistics model
        my_statistics = Statistics_Raw_Data.objects.filter(talk = my_subtitle.talk)
        for any_statistics in my_statistics:
            any_statistics.recalculate_statistics = True
            any_statistics.save()

    # If the subtitle is a translation..
    elif not my_subtitle.is_original_lang:
        my_subtitle.state_id = 11 # Translated until...
        my_subtitle.time_processed_translating = "00:00:00"

    my_subtitle.save()

    # Also reset statistics data
    my_subtitle.talk.recalculate_talk_statistics = True
    my_subtitle.talk.recalculate_speakers_statistics = True
    my_subtitle.talk.save()
    # In the Statistics model
    my_statistics = Statistics_Raw_Data.objects.filter(talk = my_subtitle.talk)
    for any_statistics in my_statistics:
        any_statistics.recalculate_statistics = True
        any_statistics.save()




# Set all states to complete and sync and sets the tweet-flags, only if not choosen otherwise
# - no matter if the subtitle is a translation or a original
def set_subtitle_complete(my_subtitle, tweet_about_it = True):
    # Stuff which need to be done anyway..
    my_subtitle.complete = True
    my_subtitle.needs_sync_to_YT = True
    my_subtitle.needs_sync_to_ftp = True
    my_subtitle.last_changed_on_amara = datetime.now(timezone.utc)

    # Only tweet if it is not a rerelease
    if tweet_about_it:
        my_subtitle.tweet = True
    else:
        my_subtitle.tweet = False

    # Stuff only if the subtitle is the orignal language
    if my_subtitle.is_original_lang:
        my_subtitle.time_processed_transcribing = my_subtitle.talk.video_duration
        my_subtitle.time_processed_syncing = my_subtitle.talk.video_duration
        my_subtitle.time_quality_check_done = my_subtitle.talk.video_duration
        my_subtitle.state_id = 8 # Complete

    # Stuff only if the subtitle is a translation
    elif not my_subtitle.is_original_lang:
        my_subtitle.time_processed_translating = my_subtitle.talk.video_duration
        my_subtitle.state_id = 12 # Translation finished

    my_subtitle.save()
    # Also reset statistics data
    my_subtitle.talk.recalculate_talk_statistics = True
    my_subtitle.talk.recalculate_speakers_statistics = True
    my_subtitle.talk.save()
    # In the Statistics model
    my_statistics = Statistics_Raw_Data.objects.filter(talk = my_subtitle.talk)
    for any_statistics in my_statistics:
        any_statistics.recalculate_statistics = True
        any_statistics.save()



basis_url = "https://amara.org/api/videos/"
anti_bot_header = {'User-Agent': 'Mozilla/5.0, Opera/9.80 (Windows NT 6.1; WOW64; U; de) Presto/2.10.289 Version/12.01',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': '',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'X-api-username': cred.AMARA_USER,
    'X-api-key': cred.AMARA_API_KEY}

# Query for all talks who have an amara key
all_talks_with_amara_key = Talk.objects.exclude(amara_key__exact = "").prefetch_related('subtitle_set').order_by("-touched")
#print(all_talks_with_amara_key.count())
for any_talk in all_talks_with_amara_key:
    # Create URL depending on amara_key
    url = basis_url+any_talk.amara_key+"/languages/?format=json"
    print(url)

    # Get json file form amara and convert to dict
    request = urllib.request.Request(url, headers = anti_bot_header)
    response = urllib.request.urlopen(request)
    encoding = response.info().get_param('charset', 'utf8')
    amara_answer = json.loads(response.read().decode(encoding))

    # Number of available subtitle languages, read from json output
    number_of_available_subtitles = amara_answer["meta"]["total_count"]

    # Get necessary info from json file for one subtitle
    subtitles_counter = 0
    while subtitles_counter < number_of_available_subtitles:
        amara_num_versions = amara_answer["objects"][subtitles_counter]["num_versions"]

        # Ignore Subtitles with no saved revision
        if amara_num_versions > 0:
            print("version in json: ",amara_num_versions)
            amara_language_code = amara_answer["objects"][subtitles_counter]["language_code"]
            amara_is_original = amara_answer["objects"][subtitles_counter]["is_primary_audio_language"]
            amara_subtitles_complete = amara_answer["objects"][subtitles_counter]["subtitles_complete"]

            language = Language.objects.get(lang_amara_short = amara_language_code)

            # Get or create subtitle entry from database
            subtitle = Subtitle.objects.get_or_create(language = language , talk = any_talk)[0]
            subtitle_was_already_complete = subtitle.complete

            # Almost only change something in the database if the version of the subtitle is not the same as before
            if (subtitle.revision != amara_num_versions):
                subtitle.is_original_lang = amara_is_original
                subtitle.revision = amara_num_versions
                subtitle.complete = amara_subtitles_complete
                subtitle.last_changed_on_amara = datetime.now(timezone.utc)
                subtitle.save()
                # Also reset statistics data
                any_talk.recalculate_talk_statistics = True
                any_talk.recalculate_speakers_statistics = True
                any_talk.save()
                # In the Statistics model
                my_statistics = Statistics_Raw_Data.objects.filter(talk = any_talk)
                for any_statistics in my_statistics:
                    any_statistics.recalculate_statistics = True
                    any_statistics.save()

                # If subtitle is orignal and new inserted into the database, set state to transcribed until..
                if (subtitle.revision == "1" and subtitle.is_original_lang):
                    subtitle.state_id = 2
                    subtitle.save()
		        # If subtitle is a translation and new inserted into the database set state to translated until..
                if (subtitle.revision == "1" and not subtitle.is_original_lang):
                    subtitle.state_id = 11
                    subtitle.save()

                # If orignal or translation and finished set state to finished
                if subtitle.complete:
                    set_subtitle_complete(subtitle, not subtitle_was_already_complete)

                # If translation and not finished set state to translation in progress
                elif (not subtitle.is_original_lang and not subtitle.complete):
                    # If the state was set to finished but isn't anymore, remove from ftp
                    # Server and reset the timestamp
                    if subtitle.state_id == 12:
                        reset_subtitle(subtitle)
                # If orignal and not finished but was set to finished, reset to transcribed until
                else:
                    # If the state was set to finished, reset to transcribed until
                    # Also reset the timestamps
                    if subtitle.state_id == 8:
                        reset_subtitle(subtitle)

            # If the revision is the same, still check the complete-Flag!
            if (subtitle.revision == amara_num_versions):
                # If the saved subtitle on amara is not complete anymore but was complete
                if not amara_subtitles_complete and subtitle.complete:
                    reset_subtitle(subtitle)
                # If the saved subtitle is not complete but amara is complete, set to complete
                if amara_subtitles_complete and not subtitle.complete:
                    set_subtitle_complete(subtitle)

        subtitles_counter += 1

print("Import Done!")

print("Checking the states..")
my_subtitles = Subtitle.objects.all().order_by("-id").select_related("state", "talk__video_duration")
# Check every Subtitle in the Database for the states if they fit the flags
for my_subtitle in my_subtitles:
    # Original language
    if my_subtitle.is_original_lang:
        # Workaround for manual setting of the time transcribed to exact the video length - doesn't work!
        if (my_subtitle.time_processed_transcribing == my_subtitle.talk.video_duration) \
            and (my_subtitle.time_processed_syncing == "00:00:00") \
            and (my_subtitle.time_quality_check_done == "00:00:00" ) \
            and (my_subtitle.blocked == False) \
            and (my_subtitle.state_id == 2): # Transcribed until..
            my_subtitle.state_id = 7
            my_subtitle.needs_automatic_syncing = True
            my_subtitle.blocked = True
            my_subtitle.save()
            print("WTF")
        # Still in transcribing process
        if my_subtitle.transcription_in_progress:
            if my_subtitle.state_id != 2:
                my_subtitle.state_id = 2 # Transcribed until...
                my_subtitle.save()
        # Still in syncing procress
        elif my_subtitle.syncing_in_progress:
            if my_subtitle.state_id != 5:
                my_subtitle.state_id = 5 # Synced until...
                my_subtitle.save()
        # Still in quality check procress
        elif my_subtitle.quality_check_in_progress:
            if my_subtitle.state_id != 7:
                my_subtitle.state_id = 7 # Quality check done until...
                my_subtitle.save()
        # Finished, depending on the time stamps
        elif my_subtitle.state_id != 2:
            if my_subtitle.state_id != 8:
                my_subtitle.state_id = 8 # Completed!
                my_subtitle.save()



    # Translation
    else:
        # Still in translating process
        if my_subtitle.translation_in_progress:
            if my_subtitle.state_id != 11:
                my_subtitle.state_id = 11 # Translated until...
                my_subtitle.save()
        # If time translated = videoduration, check if marked as finished or not
        else:
            # If marked as finished:
            if my_subtitle.complete:
                if my_subtitle.state_id != 12:
                    my_subtitle.state_id = 12 # Translation finished...
                    my_subtitle.save()
            # If subtitle is not complete but time stamps tell the opposite reset them
            else:
                 my_subtitle.time_processed_translating = "00:00:00"
                 my_subtitle.state_id = 11
                 my_subtitle.needs_removal_from_ftp = True
                 my_subtitle.needs_removal_from_YT = True
                 my_subtitle.save()

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
