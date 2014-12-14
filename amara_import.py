#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script checks for every talk with an amara key if there are updates or
# new subtitles for this talk and if so puts them in the database or updates
# them
#
# Currently missing: The setting of the "state" variables and time_processed
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

basis_url = "http://www.amara.org/api2/partners/videos/"

# Query for all talks who have an amara key
all_talks_with_amara_key = Talk.objects.exclude(amara_key__exact = "")

for any_talk in all_talks_with_amara_key:
    # Create URL depending on amara_key
    url = basis_url+any_talk.amara_key+"/languages/?format=json"
    
    # Get json file form amara and convert to dict
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    encoding = response.info().get_param('charset', 'utf8')
    amara_answer = json.loads(response.read().decode(encoding))
    
    # Number of available subtitle languages, read from json output
    number_of_available_subtitles = amara_answer["meta"]["total_count"]
        
    # Get necessary info from json file for one subtitle
    subtitles_counter = 0
    while subtitles_counter < number_of_available_subtitles:
        amara_language_code = amara_answer["objects"][subtitles_counter]["language_code"]
        amara_is_original = amara_answer["objects"][subtitles_counter]["is_original"]
        amara_num_versions = amara_answer["objects"][subtitles_counter]["num_versions"]
        amara_subtitles_complete = amara_answer["objects"][subtitles_counter]["subtitles_complete"]
        
        # Ignore Subtitles with no saved revision
        if amara_num_versions > 0:
            #print("version in json: ",amara_num_versions)
            
            # Get language connection from database
            language = Language.objects.get(lang_amara_short = amara_language_code)
            
            # Get or create subtitle entry from database
            subtitle = Subtitle.objects.get_or_create(language = language, talk = any_talk)[0]
            # Only change something in the database if the version of the subtitle is not the same as before
            if (subtitle.revision != amara_num_versions):
                #print("version in DB: ",subtitle.revision)
                #print("version in amara: ",amara_num_versions)
                subtitle.is_original_lang = amara_is_original
                subtitle.revision = amara_num_versions
                subtitle.complete = amara_subtitles_complete
                subtitle.save()

                # If orignal and finished set state to finished
                if(subtitle.is_original_lang and subtitle.complete):
                    subtitle.state_id = 8
                # If translation and finished set state to translation finished
                elif (not subtitle.is_original_lang and subtitle.complete):
                    subtitle.state_id = 12
                # If translation and not finished set state to translation in progress    
                elif (not subtitle.is_original_lang and not subtitle.complete):
                    subtitle.state_id = 11
                # If orignal and not finished but was set to finished, reset to unknown state    
                else:
                    # If the state was set to finished, reset to unknown
                    if subtitle.state_id == 8:
                        subtitle.state_id = 9
                subtitle.save()
        subtitles_counter += 1
        
print("Done!")

