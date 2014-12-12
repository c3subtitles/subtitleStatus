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
    print(number,any_talk.amara_key,len(any_talk.amara_key))
    number += 1
    url = basis_url+any_talk.amara_key+"/languages/?format=json"
    print(url)
    
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    encoding = response.info().get_param('charset', 'utf8')
    amara_answer = json.loads(response.read().decode(encoding))
    
    # Number of available subtitle languages
    available_subtitles = amara_answer["meta"]["total_count"]
    print("Menge Untertitel: ",available_subtitles)
    print("Laenge: ",len(amara_answer))
    print()
    """
    amara_answer = request.urlopen(url).read()
    print(type(amara_answer),"test")
    print(amara_answer)
    amara_answer = str(amara_answer)
    print(amara_answer)
   
    #json_file = json.JSONDecoder(amara_answer)
    json_file = json.loads(amara_answer)
    print(json_file)   
   
"""