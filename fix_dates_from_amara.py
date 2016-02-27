'''
This script gets the modification dates of subtitles from amara (http) and compares them against the dates stored in the DB.
If they differ the date from arama is written to the DB.
This fixes wrong last_changed_on_amara.date entries
'''
import os
import urllib.parse
import requests as r
import re
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Links, Tracks, Type_of, Speaker, Event, Event_Days, Rooms, Language, Subtitle, States

my_subtitles = Subtitle.objects.filter().order_by("talk_id")


for this_subtitle in my_subtitles:
    url_amara = urllib.parse.urljoin('https://www.amara.org/de/videos/', '{}/{}/'.format(this_subtitle.talk.amara_key, this_subtitle.language.lang_amara_short))

    response = r.get(url_amara)

    date_lastmod_html = re.search(r'<strong>([0-9]{2})/([0-9]{2})/([0-9]{4})</strong>', response.text)

    date_lastmod = datetime.datetime(int(date_lastmod_html.group(3)), int(date_lastmod_html.group(1)), int(date_lastmod_html.group(2)))

    set_date = False

    if date_lastmod.date() != this_subtitle.last_changed_on_amara.date():
        set_date = True


    print('id:', this_subtitle.talk.id, 'lang:', this_subtitle.language.lang_amara_short,'date_db: ', this_subtitle.last_changed_on_amara, 'date_amara: ', date_lastmod, 'set:', set_date)

    if set_date:
        this_subtitle.last_changed_on_amara = date_lastmod
        this_subtitle.save()