#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts syncs talk data to a kanboard
# It uses the kanboard library
#
# Talks which are new first need one (manual) run with the create.. function
# because of the duplicate function.
#
# This should run as cronjob roughly every 5 minutes during an event with a
# Kanboard
#==============================================================================

import os
import sys

import subtitleStatus.settings

import django
from django.conf import settings

settings.configure(**dict(
    subtitleStatus.settings.__dict__,
    DEBUG=False,
    LOGGING = {
        'version': 1,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
            },
        },
        'root': {
            'handlers': ['console'],
        }
    }
))
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

import kanboard
import time
from datetime import datetime, timezone, timedelta

from www.models import Event, Subtitle, Talk, Speaker, Talk_Persons
from www.lock import *

start = datetime.now(timezone.utc)

print("Start: ", start)

# Name and position of the columns in the angel board - might later move into the database
name_transcribing_column = "Transcription"
position_transcribing_column = 1
id_transcribing_column = 14

name_timing_column = "Timing"
position_timing_column = 2
id_timing_column = 18

name_quality_control_column = "Quality Control"
position_quality_control_column = 3
id_quality_control_column = 33

name_finished_column = "Finished!"
position_finished_column = 4
id_finished_column = 38


# Name and position of the columns in the internal board - might later move into the database
name_add_filenmame_to_db = "Filenamen in die DB eintragen"
positon_add_filenmame_to_db_column = 1
id_add_filenmame_to_db_column = 24

name_ready_for_transcription_column = "Fertig für User-Transkription"
position_ready_for_transcription_column = 8
id_ready_for_transcription_column = 36

name_transcript_needs_autotiming_column = "Transkript autotimen"
position_transcript_needs_autotiming_column = 9
id_transcript_needs_autotiming_column = 30

name_ready_for_quality_control_column = "Fertig für User Quality Control"
position_ready_for_quality_control_column = 11
id_ready_for_quality_control_column = 37

name_create_statistics_data_column = "Statistik erstellen"
position_create_statistics_data_column = 12
id_create_statistics_data_column = 32

name_special_case_do_not_touch = "Spezialfälle - keine weitere Bearbeitung nötig"
position_special_case_do_not_touch = 13
id_special_case_do_not_touch = 56

name_special_case_manual_attention_necessary = "Spezialfälle - brauchen Spezialbehandlung"
position_special_case_manual_attention_necessary = 14
id_special_case_manual_attention_necessary = 57

name_fertig_column = "Fertig!"
position_fertig_column = 15
id_fertig_column = 58

# API-KEY of admin user
API_KEY = "db03bd402e8bc0a9da581b3481af0f07823e1c012b7c4f2d34ac675a4358"

# Create a string for the involved speaker
def create_speakers_string(talk):
    speakers = Talk_Persons.objects.filter(talk = talk)
    output = ""
    if speakers.count() == 1:
        return speakers[0].speaker.name
    else:
        for any in speakers:
            output += ", " + any.speaker.name
    output = output[2:]
    return output
    
# Compare a link with description and a link list
def is_link_in_link_list(url, url_description, link_list):
    for any_entry in link_list:
        if any_entry == url_description:
            if url == link_list[any_entry]:
                return True
    return False

# Create the text for the description
def create_task_description(talk):
    # TODO Speaker fixen!
    speakers = create_speakers_string(talk)
    description = "_[This description is auto generated, manual changes might be overwritten.]_\n\n" + \
        f"**Speaker:** {speakers}\n"+ \
        f"**Language:** {talk.orig_language.language_en}\n" + \
        f"**Video duration Fahrplan:**  {talk.duration}\n" + \
        f"**Abstract:** {talk.abstract}\n\n" + \
        f"**Description:** {talk.description}\n\n" + \
        f"**Event:** {talk.event.title}\n" + \
        f"**Room:** {talk.room}\n" + \
        f"**Day:** {talk.day.index}\n" + \
        f"**Time:** {talk.start}\n" + \
        f"**Frab-ID**: {talk.frab_id_talk}\n" + \
        f"**C3Subtitles-ID**: {talk.id}\n\n" + \
        "**Links:** Please see below in the \"external Links\" section."
    return description

# Update tags for a task
# client.set_Task_Tags(project_id = 3,task_id=9,tags=["test","bla"])
def update_tags_for_a_task(client, task_id, tags, project_id = None):
    if project_id == None:
        with advisory_lock(kanboard_api_lock) as acquired:
            project_id = client.get_Task(task_id=task_id)["project_id"]
    
    # Get already applied tags
    with advisory_lock(kanboard_api_lock) as acquired:
        applied_tags = client.get_Task_Tags(task_id=task_id)
    for any in applied_tags:
        tags.append(applied_tags[any])
    with advisory_lock(kanboard_api_lock) as acquired:
        client.set_Task_Tags(project_id=project_id, task_id=task_id, tags=tags)


# Create or update the tags for a talk, works only if the tasks IDs already exist
def update_tags_for_a_talk(client, talk, tags = None):
    if tags == None:
        tags = []
        tags.append("lang:" + talk.orig_language.lang_amara_short)
        tags.append("event:" + talk.event.acronym)

    # Angel Board
    update_tags_for_a_task(client=client, task_id=talk.kanboard_public_task_id, tags=tags, project_id=talk.event.kanboard_public_project_id)
    # Internal Board
    update_tags_for_a_task(client=client, task_id=talk.kanboard_private_task_id, tags=tags, project_id=talk.event.kanboard_private_project_id)

# Create the task and the duplicate task save both IDs into the subtitleStatus database
# Create the angel task in the transcribing column, add ID to the DB
# Create the internal task in the first column, add ID to the DB
# Don't forget the tags
def create_tasks_for_a_talk(client, talk):
    if talk.kanboard_private_task_id == True and talk.kanboard_public_task_id == True:
        return None
    #Create the task on the public board
    with advisory_lock(kanboard_api_lock) as acquired:
        public_task_id = client.create_Task(title = talk.title,
            project_id = talk.event.kanboard_public_project_id,
            column_id = id_transcribing_column,
            description = create_task_description(talk=talk),
            reference = talk.id
        )
    talk.kanboard_public_task_id = public_task_id
    talk.save()
    
    # Create the links
    update_links_for_a_task(client=client, talk=talk, task_id=talk.kanboard_public_task_id)
    #update_links_for_a_task(client=client, talk=talk, task_id=talk.kanboard_private_task_id)
    
    # Duplicate the task to the internal board
    with advisory_lock(kanboard_api_lock) as acquired:
        private_task_id = client.duplicate_Task_To_Project(task_id = public_task_id,
            project_id = talk.event.kanboard_private_project_id,
            column_id=id_add_filenmame_to_db_column
        )
    talk.kanboard_private_task_id = private_task_id
    talk.save()
    # Create the tags at the end, both tasks need to exist for this
    update_tags_for_a_talk(client = client, talk = talk)
    # Create links also for the private task
    update_links_for_a_task(client=client, talk=talk, task_id=talk.kanboard_private_task_id)



# Create all links for a talk and add them / overwrite them
# Kanboard accepts the same link again!
# Link to C3Subtitles: https://c3subtitles.de/talk/<C3S-ID>
# Link to Etherpad: <talk.link_to_writable_pad>
# Link to Amara: https://amara.org/de/videos/<talk.amara_key>/
def update_links_for_a_task(client, talk, task_id):
    links = {"Link to C3Subtitles": "https://c3subtitles.de/talk/" + str(talk.id) + "/",
        "Link to the Etherpad (only for transcribing, not for quality control)": talk.link_to_writable_pad}
    if talk.amara_key != "":
        links["Link to Amara"] = "https://amara.org/de/videos/" + talk.amara_key

    # Get all links which are already online
    with advisory_lock(kanboard_api_lock) as acquired:
        links_tasks = client.get_All_External_Task_Links(task_id=task_id)
    links_online = {}
    for any in links_tasks:
        links_online[any["title"]] = any["url"]

    for any_line in links_tasks:
        # If a link which is already online is also in the links list: pass
        # Else if a link which is already online is not in the links list: remove it online
        if is_link_in_link_list(url = any_line["url"], url_description = any_line["title"], link_list=links):
            pass
        else:
            # TODO remove that link
            with advisory_lock(kanboard_api_lock) as acquired:
                client.remove_External_Task_Link(task_id = task_id, link_id = any_line["id"])

    for any_line in links:
        # If a link from the links list is also in the links online: pass
        # Else if a link from the links list is not online: add it online
        if is_link_in_link_list(url = links[any_line], url_description = any_line, link_list=links_online):
            pass
        else:
            #TODO add that link
            with advisory_lock(kanboard_api_lock) as acquired:
                client.create_External_Task_Link(task_id = task_id, url = links[any_line], title = any_line, dependency = "weblink")


# Update a task, overwrite the description and all the links
# Don't forget the tags
def update_tasks_for_a_talk(client, talk):
    # Update the description in both tasks
    with advisory_lock(kanboard_api_lock) as acquired:
        client.update_Task(id=talk.kanboard_public_task_id,
            title = talk.title,
            description = create_task_description(talk=talk),
            reference = talk.id
        )
    with advisory_lock(kanboard_api_lock) as acquired:
        client.update_Task(id=talk.kanboard_private_task_id,
            title = talk.title,
            description = create_task_description(talk=talk),
            reference = talk.id
        )
    
    # Update the tags in both tasks
    update_tags_for_a_talk(client=client, talk=talk)

    # Update the links in both tasks
    update_links_for_a_task(client=client, talk=talk, task_id=talk.kanboard_public_task_id)
    update_links_for_a_task(client=client, talk=talk, task_id=talk.kanboard_private_task_id)

# Close the internal task and open the angel task
def close_internal_open_angel_task(client, talk, public_task_is_open = None, private_task_is_open = None):
    if public_task_is_open == None or public_task_is_open == False:
        with advisory_lock(kanboard_api_lock) as acquired:
            client.open_Task(task_id = talk.kanboard_public_task_id)
    if private_task_is_open == None or private_task_is_open == True:
        with advisory_lock(kanboard_api_lock) as acquired:
            client.close_Task(task_id = talk.kanboard_private_task_id)

# Close the angel task and open the internal task
def close_angel_open_internal_task(client, talk, public_task_is_open = None, private_task_is_open = None):
    if public_task_is_open == None or public_task_is_open == True:
        with advisory_lock(kanboard_api_lock) as acquired:
            client.close_Task(task_id = talk.kanboard_public_task_id)
    if private_task_is_open == None or private_task_is_open == False:
        with advisory_lock(kanboard_api_lock) as acquired:
            client.open_Task(task_id = talk.kanboard_private_task_id)

# Close the angel task and close the internal task
def close_angel_and_close_internal_task(client, talk, public_task_is_open = None, private_task_is_open = None):
    if public_task_is_open == None or public_task_is_open == True:
        with advisory_lock(kanboard_api_lock) as acquired:
            client.close_Task(task_id = talk.kanboard_public_task_id)
    if private_task_is_open == None or private_task_is_open == True:
        with advisory_lock(kanboard_api_lock) as acquired:
            client.close_Task(task_id = talk.kanboard_private_task_id)

# Move Angel task to Transcribing
def move_angel_task_to_transcribing(client, task_id):
    # Get current positions
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to the transcribing column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_transcribing_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Move Angel task to Timing
def move_angel_task_to_timing(client, task_id):
    # Get current positions
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to the timing column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_timing_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Move Angel task to Quality control
def move_angel_task_to_quality_control(client, task_id):
    # Get current positions
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to the quality column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_quality_control_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Move Angel task to Finished and open the task to make it visible
def move_angel_task_to_finished(client, task_id):
    # Get current positions 
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to the finished column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_finished_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Move internal task to ready for transcribing
def move_internal_task_to_ready_for_transcribing(client, task_id):
    # Get current positions 
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to the finished column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_ready_for_transcription_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Move internal task to needs auto timing
def move_internal_task_to_needs_auto_timing(client, task_id):
    # Get current positions
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to the finished column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_transcript_needs_autotiming_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Move internal task to needs quality control
def move_internal_task_to_ready_for_quality_control(client, task_id):
    # Get current positions 
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to needs quality control column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_ready_for_quality_control_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Move internal task to finished
def move_internal_task_to_finished(client, task_id):
    # Get current positions 
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to the finished column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_fertig_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Move internal task to "Statistik erstellen"
def move_internal_task_to_create_statistics_data(client, task_id):
    # Get current positions 
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)
    # Move to create statistics data column
    with advisory_lock(kanboard_api_lock) as acquired:
        client.move_Task_To_Project(task_id = task_id, column_id = id_create_statistics_data_column, project_id = result["project_id"], swimlane_id = result["swimlane_id"])

# Check if a task is assigned to someone
def task_is_assigned(client, task_id):
    with advisory_lock(kanboard_api_lock) as acquired:
        data = client.get_Task(task_id = task_id)["owner_id"]
    return (data != 0)

# Check if any task of a talk is assigned
def talk_is_assigned(client, talk):
    result = task_is_assigned(client, talk.kanboard_public_task_id) or task_is_assigned(client, talk.kanboard_private_task_id)
    return result

# Check which column a task is in
def task_in_which_column(client, task_id):
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)["column_id"]
    return result

# Check if a task is open
def task_is_open(client, task_id):
    with advisory_lock(kanboard_api_lock) as acquired:
        result = client.get_Task(task_id = task_id)["is_active"]
    return result

# Check if a talk is in the transcribing process
# -> move to first column in the angel board
# Close on the internal board
def check_status_of_talk(client, talk):
    public_task_is_open = task_is_open(client, talk.kanboard_public_task_id)
    public_task_is_closed = not public_task_is_open
    private_task_is_open = task_is_open(client, talk.kanboard_public_task_id)
    private_task_is_closed = not private_task_is_open
    # If the talk has no amara link but tasks IDs than make it closed on the angel side
    # Do not change anything on the internal side apart from keeping it open
    if talk.amara_key == "":
        print("Talk-ID ohne Amara: ", talk.id)
        # Open the task on the internal board if it is not yet open
        if private_task_is_closed:
            with advisory_lock(kanboard_api_lock) as acquired:
                client.open_Task(task_id = talk.kanboard_private_task_id)
        # Close the public task if it is not yet closed
        if public_task_is_open:
            with advisory_lock(kanboard_api_lock) as acquired:
                client.close_Task(task_id = talk.kanboard_public_task_id)
    # Do nothing if any task of a talk is assigned to someone
    elif talk_is_assigned(client, talk):
        # TODO maybe check for how long it has been assigned and alarm if too long
        pass
    # Talks tasks are not assigned to anybody
    else:
        my_subtitle = Subtitle.objects.filter(talk = talk, is_original_lang = True)
        # Proceed only with talks which have a Subtitle which is the original language
        if my_subtitle.count() >= 1:
            this_subtitle = my_subtitle[0]
            print("Talk-ID:", talk.id, "Subtitle-ID:", this_subtitle.id,"Status:", this_subtitle.state.id)
            internal_task_current_column = task_in_which_column(client, talk.kanboard_private_task_id)
            public_task_current_column = task_in_which_column(client, talk.kanboard_public_task_id)
            # Check if the task is in the "Fertig für User-Transkription" Column and is still open
            # If so close it and move the user-task to the transcribing column
            if internal_task_current_column == id_ready_for_transcription_column and\
                task_is_open(client, talk.kanboard_private_task_id):
                move_angel_task_to_transcribing(client, talk.kanboard_public_task_id)
                close_internal_open_angel_task(client, talk, public_task_is_open, private_task_is_open)
            # Check if the task is in the "Fertig für User Quality Control" Column and
            # is still open
            # If so close it and move the user-task to the "Quality Control" column
            elif internal_task_current_column == id_ready_for_quality_control_column and\
                task_is_open(client, talk.kanboard_private_task_id):
                move_angel_task_to_quality_control(client, talk.kanboard_public_task_id)
                close_internal_open_angel_task(client, talk, public_task_is_open, private_task_is_open)

            # Check if the subtitle is in the transcribing process and open
            # Than it should be in column "transcribing"
            # it should be closed in the internal board and it should be in the "Fertig
            # für User-Transkriptioin Column"
            if this_subtitle.state_id == 2 and task_is_open(client, talk.kanboard_public_task_id):
                if public_task_current_column != id_transcribing_column:
                    move_angel_task_to_transcribing(client, talk.kanboard_public_task_id)
                if internal_task_current_column != id_ready_for_transcription_column:
                    move_internal_task_to_ready_for_transcribing(client, talk.kanboard_private_task_id)
                close_internal_open_angel_task(client, talk, public_task_is_open, private_task_is_open)

            # Check if the subtitle is in "waiting for auto timing" mode
            # If it also is open, close it on the user side and
            # open it on the internal board and move it to the right column
            elif this_subtitle.state_id == 4: # and task_is_open(client, talk.kanboard_public_task_id):
                if public_task_is_open:
                    with advisory_lock(kanboard_api_lock) as acquired:
                        client.close_Task(task_id = talk.kanboard_public_task_id)
                if private_task_is_closed:
                    with advisory_lock(kanboard_api_lock) as acquired:
                        client.open_Task(task_id = talk.kanboard_private_task_id)
                #close_angel_open_internal_task(client, talk)
                if internal_task_current_column != id_transcript_needs_autotiming_column:
                    move_internal_task_to_needs_auto_timing(client, talk.kanboard_private_task_id)

            # Check if the subtitle is in "quality control in progress" mode
            # If it is open it should be in the column for quality control
            # In the internal board it should be closed and in the column for
            # "ready for quality control"
            elif this_subtitle.state_id == 7:# and task_is_open(client, talk.kanboard_public_task_id):
                if public_task_current_column != id_quality_control_column:
                    move_angel_task_to_quality_control(client, talk.kanboard_public_task_id)
                if internal_task_current_column != id_ready_for_quality_control_column:
                    move_internal_task_to_ready_for_quality_control(client, talk.kanboard_private_task_id)
                close_internal_open_angel_task(client, talk, public_task_is_open, private_task_is_open)
            # Check if the subtitle is in the "quality control in progress" mode
            # and still closed in the Transcribing column
            # Open it and move it to the quality control column
            # Close the internal one and open the public one
            # Eigentlich abgebildet durch die Spalte in der es automatisch dann auf der User-
            # Seite wieder enabled wird
            #elif this_subtitle.state_id == 7 and task_is_closed(client, talk.kanboard_public_task_id):
                

            # If the Subtitle is complete - no matter if open or closed
            # Close it and if it does not yet have statistics data and is not in the
            # Spezialfälle column, move it to the "Statistik erstellen" column
            # If it is complete and it has statistics data close it on both boards and 
            # check if it is in the finished lane for the users and in the finished or 
            # Spezialfälle columns
            elif this_subtitle.state_id == 8:
                # If it has speakers statistics data move it to finished in both boards and close it
                if talk.has_speakers_statistics:
                    if internal_task_current_column != id_fertig_column:
                        move_internal_task_to_finished(client, talk.kanboard_private_task_id)
                    if public_task_current_column != id_finished_column:
                        move_angel_task_to_finished(client, talk.kanboard_public_task_id)
                    close_angel_and_close_internal_task(client, talk, public_task_is_open, private_task_is_open)
                # If is does not have speakers statistics data it should not be in the
                # "Fertig für user quality control" column but in the statistik erstellen or
                # spezialfall columns
                else:
                    # Move public task to the finished column
                    if public_task_current_column != id_finished_column:
                        move_angel_task_to_finished(client, talk.kanboard_public_task_id)
                    # Move the internal task to the create statistics data if it is not
                    # in Sonderfälle
                    if (internal_task_current_column != id_special_case_do_not_touch) and\
                        (internal_task_current_column != id_special_case_manual_attention_necessary) and\
                        internal_task_current_column != id_create_statistics_data_column:
                        move_internal_task_to_create_statistics_data(client, talk.kanboard_private_task_id)
                    close_angel_open_internal_task(client, talk, public_task_is_open, private_task_is_open)


client = kanboard.Client('https://tasks.c3subtitles.de/jsonrpc.php', 'admin', API_KEY)

# Testtalk
#talk = Talk.objects.get(id=1533)
#talk = Talk.objects.get(id=1544)
#create_tasks_for_a_talk(client, talk)
#update_tasks_for_a_talk(client, talk)

# Only talks in rC1 and rC2
#my_talks = Talk.objects.filter(Q(room__id__exact = 44) | Q(room__id__exact = 45))

# Not rC3 talks for users: 1514 is a special test-talk
talk_ids = [1225, 1252, 1274, 1281, 1303, 1238, 1254, 1288, 1282, 1342, 1333, 1305, 1313, 997, 969, 1033, 1044, 1028, 1038, 1001, 981, 983, 974, 1043, 1019, 1047, 1011, 1039, 1049, 1021, 1050, 1013, 1022, 1032, 1041, 1055, 1086, 1097, 1087, 1088, 1060, 1062, 1514]
talk_ids_2 = [1320, 1053, 1178, 1255, 1336, 1368, 1103, 1101, 1118, 1006, 1359, 1009]
#for any in talk_ids:
#    t = Talk.objects.get(id = any)
#    update_tasks_for_a_talk(client, t)
    #create_tasks_for_a_talk(client, t)
#create_tasks_for_a_talk(client, Talk.objects.get(id = 1009))

#for any_talk in my_talks:
#    update_tasks_for_a_talk(client, any_talk)
    
#update_tasks_for_a_talk(client, talk)

all_talks_with_tasks = Talk.objects.all().exclude(kanboard_private_task_id__isnull = True).exclude(kanboard_public_task_id__isnull = True).order_by("id")
#print(all_talks_with_tasks.count())
print("Betroffene Talks:", all_talks_with_tasks.count())
#"""
for any_talk in all_talks_with_tasks:
    #update_tasks_for_a_talk(client, any_talk)
    check_status_of_talk(client, any_talk)
    update_links_for_a_task(client, any_talk, any_talk.kanboard_public_task_id)
    update_links_for_a_task(client, any_talk, any_talk.kanboard_private_task_id)
#"""

#my_talk = Talk.objects.get(id=1282)
#move_internal_task_to_create_statistics_data(client,my_talk.kanboard_private_task_id)

end = datetime.now(timezone.utc)
print("Start: ", start)
print("End: ", end, "      Duration: ", end - start)
