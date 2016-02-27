import os
import urllib.parse
import requests as r
import re

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

    response_strong = str(re.search(r'<strong>[0-9]{2}/[0-9]{2}/[0-9]{4}</strong>', response.text))
    date_lastmod_html = re.search(r'[0-9]{2}/[0-9]{2}/[0-9]{4}', response_strong)
    date_lastmod_raw = date_lastmod_html.group(0)

    date_lastmod_slashed = re.sub(r'/', '-', date_lastmod_raw)
    date_lastmod = date_lastmod_slashed[-4:] + '-' + date_lastmod_slashed[0:5] + ' 12:00:00.000000+01'

    set_date = False

    if str(this_subtitle.last_changed_on_amara)[:9] is not date_lastmod[:9]:
#       this_subtitle.last_changed_on_amara = date_lastmod
#       this_subtitle.save()
        set_date = True

    print('id:', this_subtitle.talk.id, 'lang:', this_subtitle.language.lang_amara_short,'date_db: ', this_subtitle.last_changed_on_amara, 'date_amara: ', date_lastmod, 'set:', set_date)
