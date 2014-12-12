#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
number = 1

for any_talk in all_talks_with_amara_key:
    #print(number,any_talk.amara_key,len(any_talk.amara_key))
    number += 1
    url = basis_url+any_talk.amara_key+"/languages/?format=json"
    #print(url)
    
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    encoding = response.info().get_param('charset', 'utf8')
    amara_answer = json.loads(response.read().decode(encoding))
    
    # Number of available subtitle languages
    number_of_available_subtitles = amara_answer["meta"]["total_count"]
    #print("Menge Untertitel: ",number_of_available_subtitles)
    #print("Laenge: ",len(amara_answer))
    #print()
    
    # Get necessary info from json file for one subtitle
    subtitles_counter = 0
    while subtitles_counter < number_of_available_subtitles:
        amara_language_code = amara_answer["objects"][subtitles_counter]["language_code"]
        amara_is_original = amara_answer["objects"][subtitles_counter]["is_original"]
        amara_num_versions = amara_answer["objects"][subtitles_counter]["num_versions"]
        amara_subtitles_complete = amara_answer["objects"][subtitles_counter]["subtitles_complete"]
        
        #print("language_code: ",amara_language_code,type(amara_language_code))
        #print("is_original: ",amara_is_original,type(amara_is_original))
        #print("num_versions: ",amara_num_versions,type(amara_num_versions))
        #print("subtitles_complete: ",amara_subtitles_complete,type(amara_subtitles_complete))
        
        # Ignore Subtitles with no saved revision
        if amara_num_versions > 0:
            language = Language.objects.get(lang_amara_short = amara_language_code)
            subtitle = Subtitle.objects.get_or_create(language = language, talk = any_talk)[0]
            #print(type(subtitle.is_original_lang))
            subtitle.is_original_lang = amara_is_original
            subtitle.revision = amara_num_versions
            subtitle.complete = amara_subtitles_complete
            subtitle.save()
        
        subtitles_counter += 1
        
print("Done!")