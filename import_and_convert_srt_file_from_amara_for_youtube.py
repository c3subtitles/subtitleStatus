#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
#
#
#==============================================================================

import os
import sys
import urllib

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Language, Subtitle

# Search for subtitles with set flag "needs_automatic_syncing"
my_subtitles = Subtitle.objects.filter(needs_automatic_syncing = True)

for any in my_subtitles:
    language = any.language.lang_amara_short
    amara_key = any.talk.amara_key
    slug = any.talk.slug
    url = "https://www.amara.org/api2/partners/videos/"+amara_key+"/languages/"+str(language)+"/subtitles/?format=srt"
    
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    file_content = response.read()
    # Convert from bytes object to string object
    file_content = str(file_content,encoding = "UTF-8")
    
    # Split in single lines:
    text_content = file_content.splitlines()
    
    transcript = []
    transcript.append(text_content[2]+"\n")
    if text_content[3] == "":
        i = 3
    elif text_content[4] == "":
        i = 4
    elif text_content[5] == "":
        i = 5
    
    while i < len(text_content):
        # If line is empty jump two down
        if(text_content[i] == ""):
            transcript.append("\n")
            i += 3
        # If line ist not empty save to future output
        else:
            transcript.append(text_content[i]+"\n")
            i += 1
            
    filename = slug+"."+str(language)+".transcript"
    folder = "./downloads/"
    
    file = open(folder+filename,mode = "w",encoding = "utf-8")
    for line in transcript:
        file.write(line)
    file.close()

        