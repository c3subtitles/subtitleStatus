#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts checks the tasks in the kanboard if the are orphaned
# orphaned as in not connected to any talk
#
# Run this script when needed
#
#==============================================================================

import os
import sys

import subtitleStatus.settings

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

import kanboard
import time
from datetime import datetime, timezone, timedelta

from www.models import Event, Subtitle, Talk, Speaker, Talk_Persons

start = datetime.now(timezone.utc)

print("Start: ", start)

kanboards_to_check = [2,3] # all tasks from these boards
status_to_check = [0,1] # all active and inactive tasks



# API-KEY of admin user
API_KEY = "db03bd402e8bc0a9da581b3481af0f07823e1c012b7c4f2d34ac675a4358"

client = kanboard.Client('https://tasks.c3subtitles.de/jsonrpc.php', 'admin', API_KEY)

print("Tasks without connection in the database:")

for any_board in kanboards_to_check:
    print("Board:", any_board)
    for any_status in status_to_check:
        result = client.get_All_Tasks(project_id = any_board, status_id = any_status)
        for any in result:
            task_id = any["id"]
            counter = 0
            my_talks = Talk.objects.filter(kanboard_public_task_id = task_id)
            counter += my_talks.count()
            my_talks = Talk.objects.filter(kanboard_private_task_id = task_id)
            counter += my_talks.count()
            if counter == 0:
                print(any["id"], counter, any["title"])


end = datetime.now(timezone.utc)
print("Start: ", start)
print("End: ", end, "      Duration: ", end - start)
