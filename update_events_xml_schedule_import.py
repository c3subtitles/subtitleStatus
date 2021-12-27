#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script checks every event with an url to the fahrrplan in the database
# for updates depending on the version of the fahrplan
#
# In the database you can mark urls to ignore with a "#" at the beginning
#
# If the Fahrplanversion has changed everything is checked for updates
# Beware I used global vars..
#==============================================================================

import os
import sys
from lxml import etree
from urllib import request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Links, Tracks, Type_of, Speaker, Event, Event_Days, Rooms, Language, Subtitle, States, Talk_Persons
from datetime import datetime
import dateutil.parser


# Var for all urls in the database in the Event-model
url_array = []

# Array-Length depending on depth
len_day = 0
len_room = 0
len_event = 0

# Counter for every level in depth
counter_day = 0
counter_room = 0
counter_event = 0

# Error-Counter und String
error_code = 0
error_string = []

# Error Function
def error(message=""):
    global error_code, error_string
    error_code +=1
    error_string += message

# Reset everything =============================================================
def set_vars_empty(url = ""):
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration, day_index, day_date#, event_frab_prefix
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date, talk_start, talk_duration
    global talk_slug, talk_optout, talk_title, talk_subtitle, talk_track, talk_type, talk_language, talk_abstract
    global talk_description, talk_persons, talk_links, talk_guid
    global my_event, my_room, my_day, my_track, my_events, my_link, my_links, my_person, my_persons, my_type, my_language
    schedule_url = url
    schedule_version = ""
    acronym = ""
    event_title = ""
    event_start = ""
    event_end = ""
    event_days = ""
    event_frab_prefix = ""
    timeslot_duration = ""
    day_index = ""
    day_date = ""
    day_start = ""
    day_end = ""
    talk_room = ""
    talk_frab_id = -1
    talk_date = ""
    talk_start = ""
    talk_duration = ""
    talk_slug = ""
    talk_optout = False
    talk_title = ""
    talk_subtitle = ""
    talk_track = ""
    talk_type = ""
    talk_language = ""
    talk_abstract = ""
    talk_description = ""
    talk_persons = []
    talk_links = []
    talk_guid = ""
    my_event = ""
    my_room = ""
    my_day = ""
    my_track = ""
    my_events = ""
    my_link = ""
    my_links = ""
    my_person = ""
    my_persons = ""
    my_type = ""
    my_language = ""

# Vars for temporary saving ====================================================
schedule_version = ""
acronym = ""
event_title = ""
event_start = ""
event_end = ""
event_days = ""
#event_frab_prefix = ""
timeslot_duration = ""
day_index = ""
day_date = ""
day_start = ""
day_end = ""
talk_room = ""
talk_frab_id = -1
talk_date = ""
talk_start = ""
talk_duration = ""
talk_slug  = ""
talk_optout = False
talk_title = ""
talk_subtitle = ""
talk_track = ""
talk_type = ""
talk_language = ""
talk_abstract = ""
talk_description = ""
talk_persons = []
talk_links = []
talk_guid = ""
my_event = ""
my_room = ""
my_day = ""
my_track = ""
my_events = ""
my_link = ""
my_links = ""
my_person = ""
my_persons = ""
my_type = ""
my_language = ""

#===============================================================================
# Read XML and save to database functions
#===============================================================================

# Main reading/writing function
def read_xml_and_save_to_database(event_frab_prefix):
    global url_to_this_fahrplan
    set_vars_empty(url_to_this_fahrplan)
    global schedule_url, schedule_version, acronym, event_title, event_start#, event_frab_prefix
    global event_end, event_days, timeslot_duration, day_index, day_date
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date, talk_start, talk_duration
    global talk_slug, talk_optout, talk_title, talk_subtitle, talk_track, talk_type, talk_language, talk_abstract
    global talk_description, talk_persons, talk_links, talk_guid
    global fahrplan, len_day, len_event, len_room
    global counter_event, counter_event, counter_room
    global my_event, my_room, my_day, my_track, my_events, my_link, my_links, my_person, my_persons, my_type

    len_day = len(fahrplan)
    # Where in the XML start the "day" tags
    counter_day = 0

    i = 0
    while i < len(fahrplan):
        if fahrplan[i].tag == "day":
            counter_day = i
            break
        else:
            i += 1

    # Event title
    i = 0
    while i < len(fahrplan):
        j = 0
        while j < len(fahrplan[i]):
            if fahrplan[i][j].tag == "title":
                event_title = fahrplan[i][j].text
                break
            j += 1
        i += 1

    # Event schedule version
    i = 0
    while i < len(fahrplan):
        if fahrplan[i].tag == "version":
            schedule_version = fahrplan[i].text
            break
        else:
            i+=1

    # Event acronym
    i = 0
    while i < len(fahrplan):
        j = 0
        while j < len(fahrplan[i]):
            if fahrplan[i][j].tag == "acronym":
                acronym = fahrplan[i][j].text
                break
            j += 1
        i += 1

    # Event start
    i = 0
    while i < len(fahrplan):
        j = 0
        while j < len(fahrplan[i]):
            if fahrplan[i][j].tag == "start":
                event_start = fahrplan[i][j].text
                break
            j += 1
        i += 1

    # Event end
    i = 0
    while i < len(fahrplan):
        j = 0
        while j < len(fahrplan[i]):
            if fahrplan[i][j].tag == "end":
                event_end = fahrplan[i][j].text
                break
            j += 1
        i += 1

    # Event days
    i = 0
    while i < len(fahrplan):
        j = 0
        while j < len(fahrplan[i]):
            if fahrplan[i][j].tag == "days":
                event_days = fahrplan[i][j].text
                break
            j += 1
        i += 1

    # Event timeslot_duration
    i = 0
    while i < len(fahrplan):
        j = 0
        while j < len(fahrplan[i]):
            if fahrplan[i][j].tag == "timeslot_duration":
                timeslot_duration = fahrplan[i][j].text
                break
            j += 1
        i += 1

    # Write event data to database
    save_event_data()
    print("Event data saved")

    # Loop around the day tags
    while (counter_day < len_day):
        # Read day data
        if fahrplan[counter_day].tag == "day":
            day_index = fahrplan[counter_day].get("index")
            day_date =  fahrplan[counter_day].get("date")
            day_start =  fahrplan[counter_day].get("start")
            day_end =  fahrplan[counter_day].get("end")
        else:
            error("Problem with day data")

        # Write day data to database
        save_day_data()

        # Prepare for room-loop
        len_room = len(fahrplan[counter_day])
        counter_room = 0

        # Loop around the room tags
        while (counter_room < len_room):
            # Read rooom data
            if fahrplan[counter_day][counter_room].tag == "room":
                talk_room = fahrplan[counter_day][counter_room].get("name")
            else:
                error("Problem with room data")

            # Write room data to database
            save_room_data()

            # Prepare for event-loop
            len_event = len(fahrplan[counter_day][counter_room])
            counter_event = 0

            # Loop around the event tags (talks!)
            while (counter_event < len_event):
                # check how much subelements are available for this event (talk)
                len_of_tags = len(fahrplan[counter_day][counter_room][counter_event])
                counter = 0
                # Read event/talk data
                # talk_frab_id
                if fahrplan[counter_day][counter_room][counter_event].tag == "event":
                    talk_frab_id = fahrplan[counter_day][counter_room][counter_event].get("id")
                else:
                    error("Problem with talk_frab_id")

                # talk_guid
                if fahrplan[counter_day][counter_room][counter_event].tag == "event":
                    talk_guid = fahrplan[counter_day][counter_room][counter_event].get("guid")

                # talk/event_date
                if fahrplan[counter_day][counter_room][counter_event][0].tag == "date":
                    talk_date = fahrplan[counter_day][counter_room][counter_event][0].text
                elif fahrplan[counter_day][counter_room][counter_event][1].tag == "date":
                    talk_date = fahrplan[counter_day][counter_room][counter_event][1].text
                else:
                    error("Problem with event_date")

                # talk/event_start
                if fahrplan[counter_day][counter_room][counter_event][1].tag == "start":
                    talk_start = fahrplan[counter_day][counter_room][counter_event][1].text
                elif fahrplan[counter_day][counter_room][counter_event][2].tag == "start":
                    talk_start = fahrplan[counter_day][counter_room][counter_event][2].text
                else:
                    error("Problem with event_start")

                # duration
                if fahrplan[counter_day][counter_room][counter_event][2].tag == "duration":
                    talk_duration = fahrplan[counter_day][counter_room][counter_event][2].text
                elif fahrplan[counter_day][counter_room][counter_event][3].tag == "duration":
                    talk_duration = fahrplan[counter_day][counter_room][counter_event][3].text
                else:
                    error("Problem with duration")

                # slug
                if fahrplan[counter_day][counter_room][counter_event][4].tag == "slug":
                    talk_slug = fahrplan[counter_day][counter_room][counter_event][4].text
                elif fahrplan[counter_day][counter_room][counter_event][5].tag == "slug":
                    talk_slug = fahrplan[counter_day][counter_room][counter_event][5].text
                else:
                    error("Problem with slug")

                # recording optout, no bool-var!
                # start at position 0 to search for links
                counter = 0
                while fahrplan[counter_day][counter_room][counter_event][counter].tag != "recording" and counter <= len_of_tags:
                    counter += 1
                if fahrplan[counter_day][counter_room][counter_event][counter].tag == "recording":
                    talk_optout = fahrplan[counter_day][counter_room][counter_event][counter][1].text
                else:
                    error("Problem with optout")

                # talk/event_title
                # start at position 0 to search for event_title
                counter = 0
                while fahrplan[counter_day][counter_room][counter_event][counter].tag != "title" and counter <= len_of_tags:
                    counter += 1
                if fahrplan[counter_day][counter_room][counter_event][counter].tag == "title":
                    talk_title = fahrplan[counter_day][counter_room][counter_event][counter].text
                else:
                    error("Problem with event_title")

                # subtitle
                # start at position 0 to search for subtitle
                counter = 0
                while fahrplan[counter_day][counter_room][counter_event][counter].tag != "subtitle" and counter <= len_of_tags:
                    counter += 1
                if fahrplan[counter_day][counter_room][counter_event][counter].tag == "subtitle":
                    talk_subtitle = str(fahrplan[counter_day][counter_room][counter_event][counter].text)
                else:
                    error("Problem with subtitle")

                # track
                # start at position 0 to search for track
                counter = 0
                while fahrplan[counter_day][counter_room][counter_event][counter].tag != "track" and counter <= len_of_tags:
                    counter += 1
                if fahrplan[counter_day][counter_room][counter_event][counter].tag == "track":
                    talk_track = str(fahrplan[counter_day][counter_room][counter_event][counter].text)
                else:
                    error("Problem with track")

                # Write track data to database
                save_track_data()

                # type of talk
                if fahrplan[counter_day][counter_room][counter_event][9].tag == "type":
                    talk_type = str(fahrplan[counter_day][counter_room][counter_event][9].text)
                elif fahrplan[counter_day][counter_room][counter_event][10].tag == "type":
                    talk_type = str(fahrplan[counter_day][counter_room][counter_event][10].text)
                elif fahrplan[counter_day][counter_room][counter_event][11].tag == "type":
                    talk_type = str(fahrplan[counter_day][counter_room][counter_event][11].text)
                else:
                    error("Problem with type")

                # Write type of data to database
                save_type_of_data()

                # language
                if fahrplan[counter_day][counter_room][counter_event][7].tag == "language":
                    talk_language = str(fahrplan[counter_day][counter_room][counter_event][7].text)
                elif fahrplan[counter_day][counter_room][counter_event][8].tag == "language":
                    talk_language = str(fahrplan[counter_day][counter_room][counter_event][8].text)
                elif fahrplan[counter_day][counter_room][counter_event][9].tag == "language":
                    talk_language = str(fahrplan[counter_day][counter_room][counter_event][9].text)
                elif fahrplan[counter_day][counter_room][counter_event][10].tag == "language":
                    talk_language = str(fahrplan[counter_day][counter_room][counter_event][10].text)
                elif fahrplan[counter_day][counter_room][counter_event][11].tag == "language":
                    talk_language = str(fahrplan[counter_day][counter_room][counter_event][11].text)
                elif fahrplan[counter_day][counter_room][counter_event][12].tag == "language":
                    talk_language = str(fahrplan[counter_day][counter_room][counter_event][12].text)
                else:
                    error("Problem with language")
                my_language = Language.objects.get(lang_amara_short = talk_language)

                # abstract
                if fahrplan[counter_day][counter_room][counter_event][11].tag == "abstract":
                    talk_abstract = str(fahrplan[counter_day][counter_room][counter_event][11].text)
                elif fahrplan[counter_day][counter_room][counter_event][12].tag == "abstract":
                    talk_abstract = str(fahrplan[counter_day][counter_room][counter_event][12].text)
                elif fahrplan[counter_day][counter_room][counter_event][13].tag == "abstract":
                    talk_abstract = str(fahrplan[counter_day][counter_room][counter_event][13].text)
                else:
                    error("Problem with abstract")

                # description
                if fahrplan[counter_day][counter_room][counter_event][12].tag == "description":
                    talk_description = str(fahrplan[counter_day][counter_room][counter_event][12].text)
                elif fahrplan[counter_day][counter_room][counter_event][13].tag == "description":
                    talk_description = str(fahrplan[counter_day][counter_room][counter_event][13].text)
                elif fahrplan[counter_day][counter_room][counter_event][14].tag == "description":
                    talk_description = str(fahrplan[counter_day][counter_room][counter_event][14].text)
                else:
                    error("Problem with description")

                # persons (on different positions depending on schedule version)
                talk_persons = []
                # start at position 13 to search for persons
                counter = 13

                while fahrplan[counter_day][counter_room][counter_event][counter].tag != "persons" and counter <= len_of_tags:
                    counter += 1
                if fahrplan[counter_day][counter_room][counter_event][counter].tag == "persons":
                    # check if there is any subelement in persons
                    if len(fahrplan[counter_day][counter_room][counter_event][counter]):
                        for person in fahrplan[counter_day][counter_room][counter_event][counter]:
                            #talk_persons.append([int(person.get("id")), person.text])
                            talk_persons.append([person.get("id"), person.text])
                    else:
                        talk_persons = []
                else:
                    error("Problem with persons id")

                # Write persons data to database
                save_persons_data(event_frab_prefix)

                # links (on different positions depending on schedule version)
                talk_links = []
                # start at position 14 to search for links
                counter = 14

                while fahrplan[counter_day][counter_room][counter_event][counter].tag != "links" and counter <= len_of_tags:
                    counter += 1
                if fahrplan[counter_day][counter_room][counter_event][counter].tag == "links":
                    if len(fahrplan[counter_day][counter_room][counter_event][counter]):
                        for l in fahrplan[counter_day][counter_room][counter_event][counter]:
                            talk_links.append([l.get("href"), l.text])
                    else:
                        talk_links = []
                else:
                    error("Problem with links")

                # Write event/talk data to database
                save_talk_data(event_frab_prefix)

                counter_event += 1
            counter_room +=1
        counter_day += 1

# Save the data of the event into the database
def save_event_data():
    global url_to_this_fahrplan, my_event
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration

    schedule_url = url_to_this_fahrplan

    my_event = Event.objects.get(schedule_xml_link = schedule_url)
    if my_event.schedule_version != schedule_version:
        my_event.schedule_version = schedule_version
        my_event.save()
    if my_event.acronym != acronym:
        my_event.acronym = acronym
        my_event.save()
    if my_event.title != event_title:
        my_event.title = event_title
        my_event.save()
    if my_event.start != event_start:
        my_event.start = event_start
        my_event.save()
    if my_event.end != event_end:
        my_event.end = event_end
        my_event.save()
    if my_event.days != event_days:
        my_event.days = event_days
        my_event.save()
    if my_event.timeslot_duration != timeslot_duration:
        my_event.timeslot_duration = timeslot_duration
        my_event.save()

# Save the data of the days into the database
def save_day_data():
    global my_event, my_day
    global day_index, day_date, day_start, day_end
    my_day = Event_Days.objects.get_or_create(event = my_event,\
        index = day_index,\
        date = day_date)[0]
    if my_day.day_start != dateutil.parser.parse(day_start):
        my_day.day_start = day_start
        my_day.save()
    if my_day.day_end != dateutil.parser.parse(day_end):
        my_day.day_end = day_end
        my_day.save()
    if my_day.date != dateutil.parser.parse(day_date).date():
        my_day.date = day_date
        my_day.save()

# Save the data of the room into the database
def save_room_data():
    global talk_room, my_room
    my_room = Rooms.objects.get_or_create(room = talk_room)[0]
    #my_room = Rooms.objects.get(room = talk_room)

# Save the data of the speakers into the database
def save_persons_data (event_frab_prefix):
    global talk_persons, my_persons#, event_frab_prefix
    my_persons = []
    my_person = []
    for someone in talk_persons:
        my_person = Speaker.objects.get_or_create(frab_id = event_frab_prefix + str(someone[0]))[0]
        if my_person.name != someone[1]:
            my_person.name = someone[1]
            if len(my_person.name) > 50:
                my_person.name = my_person.name[0:50]
            my_person.save()

        # Array to acces all linked speakers for the saving of the talk
        my_persons.append(my_person)

# Save Tracks_of into the database (Beware, Track can be None -> as String)
def save_track_data():
    global talk_track, my_track
    my_track = Tracks.objects.get_or_create(track = talk_track)[0]

# Save Type_of into the database
def save_type_of_data():
    global talk_type, my_type
    my_type = Type_of.objects.get_or_create(type = talk_type)[0]

# Save language data into the database, not necessary!
def save_languages_data():
    pass

# Save the data of the event talk into the database
def save_talk_data (event_frab_prefix):
    global schedule_url, schedule_version, acronym, event_title, event_start#, event_frab_prefix
    global event_end, event_days, timeslot_duration, day_index, day_date
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date, talk_start, talk_duration
    global talk_slug, talk_optout, talk_title, talk_subtitle, talk_track, talk_type, talk_language, talk_abstract
    global talk_description, talk_persons, talk_links, talk_guid
    global my_event, my_room, my_day, my_track, my_events, my_link, my_links, my_person, my_persons, my_type, my_language

    my_language = Language.objects.get(lang_amara_short = talk_language)
    my_talk = []

    my_talk = Talk.objects.get_or_create(frab_id_talk = event_frab_prefix + str(talk_frab_id))[0]
    if my_talk.room != my_room:
        my_talk.room = my_room
        my_talk.save()
    if my_talk.track != my_track:
        my_talk.track = my_track
        my_talk.save()
    if my_talk.type_of != my_type:
        my_talk.type_of = my_type
        my_talk.save()
    if my_talk.orig_language != my_language:
        my_talk.orig_language = my_language
        my_talk.save()
    if my_talk.date != dateutil.parser.parse(talk_date):
        my_talk.date = talk_date
        my_talk.save()
    if my_talk.start != dateutil.parser.parse(talk_start).time():
        my_talk.start = talk_start
        my_talk.save()
    if my_talk.duration != dateutil.parser.parse(talk_duration).time():
        my_talk.duration = talk_duration
        my_talk.save()
    if my_talk.slug != talk_slug:
        my_talk.slug = talk_slug
        my_talk.save()
    if my_talk.title != talk_title:
        my_talk.title = talk_title
        my_talk.save()
    if my_talk.subtitle_talk != talk_subtitle:
        my_talk.subtitle_talk = talk_subtitle
        my_talk.save()
    if my_talk.abstract != talk_abstract:
        my_talk.abstract = talk_abstract
        my_talk.save()
    if my_talk.description != talk_description:
        my_talk.description = talk_description
        my_talk.save()
    if my_talk.guid != talk_guid:
        my_talk.guid = talk_guid
        my_talk.save()
    if my_talk.unlisted != True:
        if (talk_optout=="true"):
            my_talk.unlisted = True
            my_talk.save()
    if my_talk.unlisted == True:
        if (talk_optout != "true"):
            my_talk.unlisted = False
            my_talk.save()
    if my_talk.day != my_day:
        my_talk.day = my_day
        my_talk.save()
    if my_talk.event != my_event:
        my_talk.event = my_event
        my_talk.save()

    # Prepare to save links
    my_links = []
    my_link = []
    # Saving the links
    for some_link in talk_links:
        my_link = Links.objects.get_or_create(url = some_link[0],\
            title = some_link[1],\
            talk = my_talk)

    for any_person in my_persons:
        this_talk_persons, created = Talk_Persons.objects.get_or_create(talk = my_talk, speaker = any_person)
        #this_talk_persons.save()


#===============================================================================
# Main
#===============================================================================

# Get all schedule-urls from the database
my_events = Event.objects.all()
for e in my_events:
    fahrplan_link = e.schedule_xml_link
    # Only if the fahrplan field is not empty and doesn't start with an "#"
    if fahrplan_link != "" and fahrplan_link[0] != '#':
        url_array.append(fahrplan_link)

    # For later comparison if necessary
    e.save_fahrplan_xml_file()

# For every fahrplan file
for url_to_this_fahrplan in url_array:
    response = request.urlopen(url_to_this_fahrplan)
    tree = etree.parse(response)
    fahrplan = tree.getroot()

    # Compare Fahrplanversion in the database and online, break if the same:
    this_event = Event.objects.get(schedule_xml_link = url_to_this_fahrplan)
    i = 0
    while i < len(fahrplan):
        if fahrplan[i].tag == "version":
            fahrplan_version = fahrplan[i].text
            break
        else:
            i+=1
        print(i)
    i = 0
    while i < len(fahrplan):
        j = 0
        while j < len(fahrplan[i]):
            if fahrplan[i][j].tag == "title":
                fahrplan_title = fahrplan[i][j].text
                break
            j += 1
        i += 1
    if fahrplan_version == this_event.schedule_version:
        print("In ",fahrplan_title," nichts geändert! Version ist: ",fahrplan_version)
        continue
    else:
        print("In ",fahrplan_title," etwas geändert!\nVon Version: \"",this_event.schedule_version,"\" to \"",fahrplan_version,"\"")
    #print("Debug Event:",fahrplan[1][0].text)
    #print("Debug: Version in DB: ", this_event.schedule_version,"\n\n")

    #Funktion für Fahrplan in Datenbank schubsen
    read_xml_and_save_to_database(event_frab_prefix = this_event.frab_id_prefix)

print ("Durch gelaufen, Error Code: ", error_code)
print ("Fehler: ",error_string)
