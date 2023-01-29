#!/usr/bin/python3
# -*- coding: utf-8 -*-

# =============================================================================
# This script checks every event with an url to the fahrrplan in the database
# for updates depending on the version of the fahrplan
#
# In the database you can mark urls to ignore with a "#" at the beginning
#
# If the Fahrplanversion has changed everything is checked for updates
# Beware I used global vars..
# =============================================================================

import django
import os
import sys
from lxml import etree
from urllib import request
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
import dateutil.parser

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")
django.setup()
from www.models import (
    Talk,
    Links,
    Tracks,
    Type_of,
    Speaker,
    Event,
    Event_Days,
    Rooms,
    Language,
    Subtitle,
    States,
    Talk_Persons
)


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

event_error_counter = 0
global_error_counter = 0


# Reset everything =============================================================
def set_vars_empty(url=""):
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration, day_index, day_date
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date
    global talk_start, talk_duration, talk_slug, talk_optout, talk_title
    global talk_subtitle, talk_track, talk_type, talk_language, talk_abstract
    global talk_description, talk_persons, talk_links, talk_guid
    global my_event, my_room, my_day, my_track, my_events, my_link, my_links
    global my_person, my_persons, my_type, my_language, event_error_counter
    global global_error_counter
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
    global_error_counter += event_error_counter
    event_error_counter = 0


# Vars for temporary saving ===================================================
schedule_version = ""
acronym = ""
event_title = ""
event_start = ""
event_end = ""
event_days = ""
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

# ==============================================================================
# Read XML and save to database functions
# ==============================================================================


# Main reading/writing function
def read_xml_and_save_to_database(event_frab_prefix):
    global url_to_this_fahrplan
    set_vars_empty(url_to_this_fahrplan)
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration, day_index, day_date
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date, talk_start
    global talk_duration, talk_slug, talk_optout, talk_title, talk_subtitle, talk_track
    global talk_type, talk_language, talk_abstract, talk_description, talk_persons
    global talk_links, talk_guid, fahrplan, len_day, len_event, len_room
    global counter_event, counter_event, counter_room
    global my_event, my_room, my_day, my_track, my_events, my_link, my_links, my_person
    global my_persons, my_type, event_error_counter

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
            i += 1

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

    # Write event data to database but do not update the version, only if there were no
    # breaking errors
    save_event_data(update_fahrplan_version=False)
    print("Info: Event data saved, no version update:", event_title)

    # Loop around the day tags
    while (counter_day < len_day):
        # Read day data
        if fahrplan[counter_day].tag == "day":
            day_index = fahrplan[counter_day].get("index")
            day_date = fahrplan[counter_day].get("date")
            day_start = fahrplan[counter_day].get("start")
            day_end = fahrplan[counter_day].get("end")
        else:
            print("Error: Problem with day data. Day has been ignored.")
            event_error_counter += 1
            continue

        # Write day data to database
        save_day_data()
        print("Info: Day data saved:", day_index, day_date, day_start, day_end)

        # Prepare for room-loop
        len_room = len(fahrplan[counter_day])
        counter_room = 0

        # Loop around the room tags
        while (counter_room < len_room):
            # Read rooom data
            if fahrplan[counter_day][counter_room].tag == "room":
                talk_room = fahrplan[counter_day][counter_room].get("name")
            else:
                print("Error: Problem with room data. Room as been ignored.")
                event_error_counter += 1
                continue

            # Write room data to database
            save_room_data()
            print("Info: Room data saved:", talk_room)

            # Prepare for event-loop
            len_event = len(fahrplan[counter_day][counter_room])
            counter_event = 0

            # Loop around the event tags (talks!)
            while (counter_event < len_event):
                # Read event/talk data
                # talk_frab_id
                if fahrplan[counter_day][counter_room][counter_event].tag == "event":
                    talk_frab_id = fahrplan[counter_day][counter_room][
                        counter_event
                    ].get("id")
                    talk_guid = fahrplan[counter_day][counter_room][counter_event].get(
                        "guid"
                    )
                else:
                    print("Error: Problem with talk_frab_id or talk_guid")
                    event_error_counter += 1
                    continue

                # check how much subelements are available for this event (talk)
                len_of_tags = len(fahrplan[counter_day][counter_room][counter_event])
                counter = 0

                # Reset all vars to see if one was not set
                talk_date = None
                talk_start = None
                talk_duration = None
                talk_slug = None
                talk_optout = None
                talk_title = None
                talk_subtitle = None
                talk_track = None
                talk_type = None
                talk_language = None
                talk_abstract = None
                talk_description = None
                talk_persons = []
                talk_links = []
                # Loop over all tags below an event
                while counter < len_of_tags:
                    # talk/event_date
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "date"
                    ):
                        talk_date = fahrplan[counter_day][counter_room][counter_event][
                            counter
                        ].text

                    # talk/event_start
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "start"
                    ):
                        talk_start = fahrplan[counter_day][counter_room][counter_event][
                            counter
                        ].text

                    # duration
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "duration"
                    ):
                        talk_duration = fahrplan[counter_day][counter_room][
                            counter_event
                        ][counter].text

                    # slug
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "slug"
                    ):
                        talk_slug = fahrplan[counter_day][counter_room][counter_event][
                            counter
                        ].text

                    # recording optout, no bool-var!
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "recording"
                    ):
                        talk_optout = fahrplan[counter_day][counter_room][
                            counter_event
                        ][counter][1].text

                    # talk/event_title
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "title"
                    ):
                        talk_title = fahrplan[counter_day][counter_room][counter_event][
                            counter
                        ].text

                    # subtitle
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "subtitle"
                    ):
                        talk_subtitle = str(
                            fahrplan[counter_day][counter_room][counter_event][
                                counter
                            ].text
                        )

                    # track
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "track"
                    ):
                        talk_track = str(
                            fahrplan[counter_day][counter_room][counter_event][
                                counter
                            ].text
                        )
                        # Write track data to database
                        save_track_data()

                    # type of talk
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "type"
                    ):
                        talk_type = str(
                            fahrplan[counter_day][counter_room][counter_event][
                                counter
                            ].text
                        )
                        # Write type of data to database
                        save_type_of_data()

                    # language
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "language"
                    ):
                        talk_language = str(
                            fahrplan[counter_day][counter_room][counter_event][
                                counter
                            ].text
                        )
                        my_language = Language.objects.get(
                            lang_amara_short=talk_language
                        )

                    # abstract
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "abstract"
                    ):
                        talk_abstract = str(
                            fahrplan[counter_day][counter_room][counter_event][
                                counter
                            ].text
                        )

                    # description
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "description"
                    ):
                        talk_description = str(
                            fahrplan[counter_day][counter_room][counter_event][
                                counter
                            ].text
                        )

                    # persons (on different positions depending on schedule version)
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "persons"
                    ):
                        # check if there is any subelement in persons
                        if len(fahrplan[counter_day][counter_room][counter_event][
                            counter
                        ]):
                            for person in fahrplan[counter_day][counter_room][
                                counter_event
                            ][counter]:
                                talk_persons.append([person.get("id"), person.text])
                        # Write persons data to database
                        save_persons_data(event_frab_prefix)

                    # links (on different positions depending on schedule version)
                    if (
                        fahrplan[counter_day][counter_room][counter_event][counter].tag
                        == "links"
                    ):
                        if len(fahrplan[counter_day][counter_room][counter_event][
                            counter
                        ]):
                            for link_element in fahrplan[counter_day][counter_room][
                                counter_event
                            ][counter]:
                                talk_links.append(
                                    [link_element.get("href"), link_element.text]
                                )

                    counter += 1

                # Check a few variables for plausibility which will cause an error:
                if talk_date is None:
                    print(
                        "Error: Talk with frab_id",
                        talk_frab_id,
                        "has no date. This talk data will not be saved."
                    )
                    continue
                if talk_start is None:
                    print(
                        "Error: Talk with frab_id",
                        talk_frab_id,
                        "has no start. This talk data will not be saved."
                    )
                    continue
                if talk_duration is None:
                    print(
                        "Error: Talk with frab_id",
                        talk_frab_id,
                        "has no duration. This talk data will not be saved.")
                    continue
                if talk_slug is None:
                    print(
                        "Error: Talk with frab_id",
                        talk_frab_id,
                        "has no slug. This talk data will not be saved."
                    )
                    continue
                if talk_language is None:
                    print(
                        "Error: Talk with frab_id",
                        talk_frab_id,
                        "has no language. This talk data will not be saved."
                    )
                    continue
                # Check a few variables for plausibility which will cause a warning:
                if talk_title is None:
                    print("Warning: Talk with frab_id", talk_frab_id, "has no title.")
                if talk_subtitle is None:
                    print(
                        "Warning: Talk with frab_id", talk_frab_id, "has no subtitle."
                    )
                if talk_abstract is None:
                    print(
                        "Warning: Talk with frab_id", talk_frab_id, "has no abstract."
                    )
                if talk_description is None:
                    print(
                        "Warning: Talk with frab_id",
                        talk_frab_id,
                        "has no description."
                    )
                if talk_track is None:
                    print("Warning: Talk with frab_id", talk_frab_id, "has no track.")
                if talk_type is None:
                    print("Warning: Talk with frab_id", talk_frab_id, "has no type.")
                if talk_optout is None:
                    print("Warning: Talk with frab_id", talk_frab_id, "has no optout.")
                if talk_persons == []:
                    print(
                        "Warning: Talk with frab_id", talk_frab_id, "has no speakers."
                    )
                if talk_links == []:
                    print("Warning: Talk with frab_id", talk_frab_id, "has no links.")

                # Write event/talk data to database
                save_talk_data(event_frab_prefix)
                print("Info: Talk with frab_id", talk_frab_id, "has been saved.")

                counter_event += 1
            counter_room += 1
        counter_day += 1

    # Write event data to database and update the version
    # since there were no breaking errors
    if event_error_counter == 0:
        save_event_data(update_fahrplan_version=True)
        print("Info: Event data saved with version update:", event_title)
    else:
        print(
            "Error: Event data not saved with version update because of errors:",
            event_title
        )


# Save the data of the event into the database
def save_event_data(update_fahrplan_version=True):
    global url_to_this_fahrplan, my_event
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration

    schedule_url = url_to_this_fahrplan

    my_event = Event.objects.get(schedule_xml_link=schedule_url)
    if update_fahrplan_version and (my_event.schedule_version != schedule_version):
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
    my_day = Event_Days.objects.get_or_create(
        event=my_event, index=day_index, date=day_date
    )[0]
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
    my_room = Rooms.objects.get_or_create(room=talk_room)[0]


# Save the data of the speakers into the database
def save_persons_data(event_frab_prefix):
    global talk_persons, my_persons  # , event_frab_prefix
    my_persons = []
    my_person = []
    for someone in talk_persons:
        my_person = Speaker.objects.get_or_create(
            frab_id=event_frab_prefix + str(someone[0])
        )[0]
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
    my_track = Tracks.objects.get_or_create(track=talk_track)[0]


# Save Type_of into the database
def save_type_of_data():
    global talk_type, my_type
    my_type = Type_of.objects.get_or_create(type=talk_type)[0]


# Save language data into the database, not necessary!
def save_languages_data():
    pass


# Save the data of the event talk into the database
def save_talk_data(event_frab_prefix):
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration, day_index, day_date
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date, talk_start
    global talk_duration, talk_slug, talk_optout, talk_title, talk_subtitle, talk_track
    global talk_type, talk_language, talk_abstract, talk_description, talk_persons
    global talk_links, talk_guid, my_event, my_room, my_day, my_track, my_events
    global my_link, my_links, my_person, my_persons, my_type, my_language

    my_language = Language.objects.get(lang_amara_short=talk_language)
    my_talk = []

    my_talk = Talk.objects.get_or_create(
        frab_id_talk=event_frab_prefix + str(talk_frab_id)
    )[0]
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
    if my_talk.unlisted is not True:
        if (talk_optout == "true"):
            my_talk.unlisted = True
            my_talk.save()
    if my_talk.unlisted is True:
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
        my_link = Links.objects.get_or_create(
            url=some_link[0], title=some_link[1], talk=my_talk
        )

    # Save the connection between a talk and a speaker
    for any_person in my_persons:
        this_talk_persons, created = Talk_Persons.objects.get_or_create(
            talk=my_talk, speaker=any_person
        )


# ==============================================================================
# Main
# ==============================================================================

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
    this_event = Event.objects.get(schedule_xml_link=url_to_this_fahrplan)
    i = 0
    while i < len(fahrplan):
        if fahrplan[i].tag == "version":
            fahrplan_version = fahrplan[i].text
            break
        else:
            i += 1
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
        print(
            "No changes in",
            '"' + fahrplan_title + '"',
            "Version is still:",
            '"' + fahrplan_version + '"',
        )
        continue
    else:
        print(
            "Changes in",
            '"' + fahrplan_title + '"',
            "From Version:",
            '"' + this_event.schedule_version + '"',
            "to",
            '"' + fahrplan_version + '"'
        )

    # Funktion für Fahrplan in Datenbank schubsen
    read_xml_and_save_to_database(event_frab_prefix=this_event.frab_id_prefix)

print("Script finished, Sum of errors over all Fahrpläne: ", global_error_counter)

