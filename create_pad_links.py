'''
This script helps to set the pad Links for every talks of an event.
You need to set:
event_id = your event
short_id = Short ID for the event
overwrite = True or False
You NEED to manualy set the short_id for events other than "the" Congress, else there might be conflicts, sometimes the Fahrplanimport overwrites the specific acronym
You MIGHT need to change the creation of the link for events other than the congress, else the long frab_id_talk will be in the link, the link would have the event double
'''
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")
import django

django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Links, Tracks, Type_of, Speaker, Event, Event_Days, Rooms, Language, Subtitle, States

#36c3
#event_id = 11
#36c3-chaoswest
event_id=12
#36c3-wikipaka
#event_id=13
event = Event.objects.get(id=event_id)
overwrite = True

#short_id = event.acronym
short_id = "36c3-chaoswest"
#short_id = "36c3-wikipaka"

my_talks = Talk.objects.filter(event = event)
print(my_talks.count())

for any in my_talks:
    if overwrite:
        any.link_to_writable_pad = "https://subtitles.pads.ccc.de/" + short_id + "-talk-" + any.frab_id_talk.split("-")[-1]
        print(any.link_to_writable_pad)
        any.save()
    else:
        if any.link_to_writable_pad == "":
            any.link_to_writable_pad = "https://subtitles.pads.ccc.de/" + short_id + "-talk-" + any.frab_id_talk.split("-")[-1]
            any.save()
            print(any.link_to_writable_pad)
