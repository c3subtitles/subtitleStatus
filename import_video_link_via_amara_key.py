#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script imports the video links into the database
# language table in the columns lang_amara_short and lang_en
# The amara data is available here:
# http://www.amara.org/api2/partners/languages/?format=json
#==============================================================================

import os
import sys
from lxml import etree
import urllib
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk

basis_url = "http://www.amara.org/api2/partners/videos/"

my_talks = Talk.objects.exclude(amara_key = "")

for any_talk in my_talks:
    # Create URL depending on amara_key
    url = basis_url + any_talk.amara_key + "/?format=json"
    
    # Get json file form amara and convert to dict
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    encoding = response.info().get_param('charset', 'utf8')
    amara_answer = json.loads(response.read().decode(encoding))
    
    # Save into database
    any_talk.link_to_video_file = amara_answer["all_urls"][0]
    any_talk.save()
 
print ("done")