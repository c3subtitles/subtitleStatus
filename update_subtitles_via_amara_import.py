#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script checks for every talk with an amara key if there are updates or
# new subtitles for this talk and if so puts them in the database or updates
# them
#
# Currently missing: The setting of the corresponding timestamps
#
#==============================================================================

import os
import sys
import json
import urllib.request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Language, Subtitle, States

import credentials as cred

basis_url = "http://www.amara.org/api2/partners/videos/"
anti_bot_header = {'User-Agent': 'Mozilla/5.0, Opera/9.80 (Windows NT 6.1; WOW64; U; de) Presto/2.10.289 Version/12.01',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': '',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'X-api-username': cred.AMARA_USER,
    'X-api-key': cred.AMARA_API_KEY}

# Query for all talks who have an amara key
all_talks_with_amara_key = Talk.objects.exclude(amara_key__exact = "").select_related("Subtitle").select_related("Subtitle__talk")
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
            #print("version in json: ",amara_num_versions)
            amara_language_code = amara_answer["objects"][subtitles_counter]["language_code"]
            amara_is_original = amara_answer["objects"][subtitles_counter]["is_original"]
            amara_subtitles_complete = amara_answer["objects"][subtitles_counter]["subtitles_complete"]

            language = Language.objects.get(lang_amara_short = amara_language_code)
            
            # Get or create subtitle entry from database
            subtitle = Subtitle.objects.get_or_create(language = language , talk = any_talk)[0]
            # Only change something in the database if the version of the subtitle is not the same as before            
            if (subtitle.revision != amara_num_versions):
                subtitle.is_original_lang = amara_is_original
                subtitle.revision = amara_num_versions
                subtitle.complete = amara_subtitles_complete
                subtitle.save()
                
                # If subtitle is orignal and new inserted into the database, set state to transcribed until..
                if(subtitle.revision == "1" and subtitle.is_original_lang):
                    subtitle.state_id = 2

                # If orignal and finished set state to finished
                if(subtitle.is_original_lang and subtitle.complete):
                    subtitle.state_id = 8
                    subtitle.time_processed_transcribing = subtitle.talk.video_duration
                    subtitle.time_processed_syncing = subtitle.talk.video_duration
                    subtitle.time_quality_check_done = subtitle.talk.video_duration
                    subtitle.needs_sync_to_ftp = True
                # If translation and finished set state to translation finished
                elif (not subtitle.is_original_lang and subtitle.complete):
                    subtitle.state_id = 12
                    subtitle.time_processed_translating = subtitle.talk.video_duration
                    subtitle.needs_sync_to_ftp = True
                # If translation and not finished set state to translation in progress    
                elif (not subtitle.is_original_lang and not subtitle.complete):
                    # If the state was set to finished but isn't anymore, remove from ftp
                    # Server and reset the timestamp
                    if subtitle.state_id == 12:
                        subtitle.needs_removal_from_ftp = True
                        subtitle.time_processed_translating = "00:00:00"
                    subtitle.state_id = 11
                # If orignal and not finished but was set to finished, reset to transcribed until
                else:
                    # If the state was set to finished, reset to transcribed until
                    # Also reset the timestamps
                    if subtitle.state_id == 8:
                        subtitle.state_id = 2
                        subtitle.time_processed_transcribing = "00:00:00"
                        subtitle.time_processed_syncing = "00:00:00"
                        subtitle.time_processed_quality_check_done = "00:00:00" 
                        subtitle.needs_removal_from_ftp = True
                        
                subtitle.save()
                
        subtitles_counter += 1

print("Import Done!")

print("Checking the states..")
my_subtitles = Subtitle.objects.all().order_by("-id").select_related("States").select_related("talk__video_duration")
# Check every Subtitle in the Database for the states if they fit the flags
for my_subtitle in my_subtitles:
    # Original language
    if my_subtitle.is_original_lang:
        # Still in transcribing process
        if my_subtitle.time_processed_transcribing < my_subtitle.talk.video_duration:
            if my_subtitle.state_id != 2:
                my_subtitle.state_id = 2 # Transcribed until...
                my_subtitle.save()
        # Still in syncing procress
        elif my_subtitle.time_processed_syncing < my_subtitle.talk.video_duration:
            if my_subtitle.state_id != 5:
                my_subtitle.state_id = 5 # Synced until...
                my_subtitle.save()
        # Still in quality check procress
        elif my_subtitle.time_quality_check_done < my_subtitle.talk.video_duration:
            if my_subtitle.state_id != 7:
                my_subtitle.state_id = 7 # Quality check done until...
                my_subtitle.save()
        # Finished, depending on the time stamps
        else:
            if my_subtitle.state_id != 8:
                my_subtitle.state_id = 8 # Completed!
                my_subtitle.save()
    # Translation
    else:
        # Still in translating process
        if my_subtitle.time_processed_translating < my_subtitle.talk.video_duration:
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
                 my_subtitle.save()
print(".. done!")