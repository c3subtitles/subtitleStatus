#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script imports data into the database from CSV Files
#==============================================================================

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk

if len(sys.argv) < 2:
    sys.exit("Not enough arguments! Filename needed!")

read_file = open(sys.argv[1], mode = "r", encoding = "utf-8")
file_content = read_file.read()
text_content = file_content.splitlines()
text_content_separated=[]
for line in text_content:
    new_line = line.split(';')
    text_content_separated.append(new_line)
	
for line in text_content_separated:
    print(len(line),line)
    try:
        my_talk = Talk.objects.get(frab_id_talk = int(line[0]))
        my_talk.amara_key = line[2]
        my_talk.youtube_key = line[3]
        my_talk.video_duration = line[4]
        my_talk.link_to_video_file = line[6]
        my_talk.save()
    except ObjectDoesNotExist:
	    print(line[0]+" gibts nicht!")
