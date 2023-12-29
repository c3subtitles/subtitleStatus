#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script creates text for bots and sends those messages to the bots
# It is usable with Twitter, Mastodon, IRC, Rocketchat, ...
#==============================================================================

import os
import requests
"""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")
import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
"""

from mastodon import Mastodon
import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from subprocess import Popen, PIPE

#from www.models import *
import credentials as cred

"""
# Use this code to recreate the tokens for Mastodon:
Mastodon.create_app(
    "c3subtitles_releasing_bot",
    api_base_url = cred.MT_C3R_TOKEN_FILENAME,
    to_file = cred.MT_C3R_TOKEN_FILENAME
)
mastodon.log_in(
    cred.MT_C3R_EMAIL,
    'incrediblygoodpassword',
    to_file = cred.MT_C3R_TOKEN_FILENAME
)
Mastodon.create_app(
    "c3subtitles_progress_bot",
    api_base_url = cred.MT_C3P_TOKEN_FILENAME,
    to_file = cred.MT_C3P_TOKEN_FILENAME
)
mastodon.log_in(
    cred.MT_C3P_EMAIL,
    'incrediblygoodpassword',
    to_file = cred.MT_C3P_TOKEN_FILENAME
)
"""

# Mastodon
mastodon_c3srt_progress = Mastodon(
    access_token = os.path.join(os.path.dirname(os.path.dirname(__file__)),"credentials", cred.MT_C3P_TOKEN_FILENAME),
    api_base_url = cred.MT_C3P_API_BASE_URL
    )

mastodon_c3srt_releasing = Mastodon(
    access_token = os.path.join(os.path.dirname(os.path.dirname(__file__)),"credentials", cred.MT_C3R_TOKEN_FILENAME),
    api_base_url = cred.MT_C3R_API_BASE_URL
    )

# Message Parameters for some special cases like Twitter and Mastodon with
# maximum Character Settings and Link Length char settings
message_parameters = {
    "Twitter": {
        "max_chars": 280,
        "links_char_length": 23
        },
    "Mastodon": {
        "max_chars": 500,
        "links_char_length": 23
        }
    }

# Create a tweet for a subtitle which is now available with transcript
def create_text_for_transcript_is_now_available(my_talk, text_format = "Twitter"):
    # Check if there really is a talk available with this Id:
    try:
        my_language = my_talk.orig_language
        my_event = my_talk.event
    except:
        return(None)

    # Workaround for Klingon :D
    if my_language.id == 289:
        my_language.language_en = "Original"
    lang_string = my_language.language_en
    name_of_talk = my_talk.title
    hashtags = my_event.hashtag
    link = "https://c3subtitles.de/talk/" + str(my_talk.id)
    # Test : The [language] talk "talk title" now has a transcript available for you to work on.
    # Join us here: c3s-link
    # Hashtags
    if text_format == "Twitter" or text_format == "Mastodon":
        link_counts_as = message_parameters[text_format]["links_char_length"]
        max_text_length = message_parameters[text_format]["max_chars"]
    # Length of Text consists of the length of the strings and n characters for a link
        while len("The ") + len(lang_string) + len(" talk \"") + len(name_of_talk) + len("\" now has a transcript available for you to work on. Join us here: ") + link_counts_as + 2 + len(hashtags) > max_text_length:
            name_of_talk = name_of_talk[:-2]
            name_of_talk = name_of_talk + "…"

    text = "The " + lang_string + " talk \"" + name_of_talk + "\" now has a transcript available for you to work on. Join us here: https://c3subtitles.de/talk/" + str(my_talk.id) + " " + hashtags

    return text

def create_text_for_subtitle_needs_timing(my_subtitle):
    text = "The " + my_subtitle.language.language_en + " talk \"" + my_subtitle.talk.title + "\" needs timing: https://c3subtitles.de/talk/" + str(my_subtitle.talk.id) + " " + my_subtitle.talk.link_to_writable_pad + " " + "https://c3subtitles.de/admin/www/talk/" + str(my_subtitle.talk.id) + " " + "https://studio.youtube.com/video/" + my_subtitle.talk.c3subtitles_youtube_key + "/translations" + " " + "https://amara.org/videos/" + my_subtitle.talk.amara_key + " " + "https://c3subtitles.de/workflow/transforms/" + str(my_subtitle.id) + " " + "https://c3subtitles.de/admin/www/subtitle/" + str(my_subtitle.id) + " " + "https://c3subtitles.de/admin/www/subtitle/?q=" + str(my_subtitle.id)
    return text

def create_text_for_subtitle_ready_for_quality_control(my_subtitle, text_format = "Text"):
    # Get associated Data from the database
    try:
        my_language = my_subtitle.language
    except:
        return(None)
    # Workaround for Klingon :D
    if my_language.id == 289:
        my_language.language_en = "Original"
    string = my_language.language_en + " #subtitles for "
    name_of_talk = my_subtitle.talk.title
    hashtag = my_subtitle.talk.event.hashtag
    link = "https://c3subtitles.de/talk/" + str(my_subtitle.talk_id)
    # Length of the text is the actual string length and x chars per link
    if text_format == "Twitter" or text_format == "Mastodon":
        link_counts_as = message_parameters[text_format]["links_char_length"]
        max_text_length = message_parameters[text_format]["max_chars"]
        while len(string) + 1 + len(name_of_talk) + 35 + link_counts_as + 1 + len(hashtag) > max_text_length:
            name_of_talk = name_of_talk[:-2]
            name_of_talk = name_of_talk + "…"
        
    text = string + '"' + name_of_talk + '" need to be reviewed! Join us on: ' + link + " " + hashtag
    return text


def create_text_for_subtitle_is_released(my_subtitle, text_format = "Text"):
    # Check if the file really is on the mirror and only then proceed
    # The calling function has to do this

    # Get associated Data from the database
    try:
        my_language = my_subtitle.language
    except:
        return(None)

    # Workaround for Klingon :D
    if my_language.id == 289:
        my_language.language_en = "Original"
    string = my_language.language_en + " #subtitles released for "
    name_of_talk = my_subtitle.talk.title
    hashtag = my_subtitle.talk.event.hashtag
    link = "https://mirror.selfnet.de/c3subtitles/" + my_subtitle.talk.event.subfolder_in_sync_folder
    # Length of the text is the actual string length and x chars per link
    if text_format == "Twitter" or text_format == "Mastodon":
        link_counts_as = message_parameters[text_format]["links_char_length"]
        max_text_length = message_parameters[text_format]["max_chars"]
        while len(string) + 4 + len(name_of_talk) + 3 + link_counts_as + len(hashtag) + 1 > max_text_length:
            name_of_talk = name_of_talk[:-2]
            name_of_talk = name_of_talk + "…"

    text = string + '"' + name_of_talk + '" on: ' + link + " " + hashtag
    return text

def create_and_send_email_for_subtitle_needs_autotiming(my_subtitle):
    FROM = cred.E_MAIL_FROM
    TO = cred.E_MAIL_TO_FOR_TRANSCRIPTS_TIMING
    TEXT = []
    TEXT.append("These Subtitle-Files need your attention: ")

    language = my_subtitle.language.lang_amara_short
    amara_key = my_subtitle.talk.amara_key
    slug = my_subtitle.talk.slug
    url = "https://amara.org/api2/partners/videos/"+amara_key+"/languages/"+str(language)+"/subtitles/?format=srt"

    # Building the email
    msg = MIMEMultipart()

    # Fix für keinen Video-Link in der DB
    video_link = my_subtitle.talk.link_to_video_file

    # Build text for email with important Links
    text = MIMEText("Talk: "+my_subtitle.talk.title+" \n"+
        "Talk-ID: "+str(my_subtitle.talk.id)+"\n"+
        "Subtitle-ID: "+str(my_subtitle.id)+"\n"+
        "Subtitle-Sprache: " + language + "\n\n" +
        "Pad writable link: " + my_subtitle.talk.link_to_writable_pad + "\n" +
        "Direkte Transforms-Adresse: https://c3subtitles.de/workflow/transforms/" + str(my_subtitle.id) + "/\n" +
        "Direkte Admin-Subtitle-Adresse: https://c3subtitles.de/admin/www/subtitle/" + str(my_subtitle.id) + "\n" +
        "YouTube direkte Untertitel-Adresse: https://studio.youtube.com/video/" + my_subtitle.talk.c3subtitles_youtube_key +"/translations\n" +
        "Amara-Adresse: "+"https://amara.org/videos/"+my_subtitle.talk.amara_key+"/ \n" +
        "Admin-Subtitle-Adresse: https://c3subtitles.de/admin/www/subtitle/?q=" + str(my_subtitle.id) + "\n\n" +
        "YouTube-Adresse im C3Subtitles YT-Account: https://www.youtube.com/watch?v=" + my_subtitle.talk.c3subtitles_youtube_key + "\n" +
        "Talk-Adresse bei uns: https://c3subtitles.de/talk/" + str(my_subtitle.talk.id) + "\n" +
        "Admin-Talk-Adresse: https://c3subtitles.de/admin/www/talk/" + str(my_subtitle.talk.id) + "\n" +
        "Adminer-Adresse: http://adminer.c3subtitles.de/?pgsql=&db=subtitlestatus&ns=public&edit=www_subtitle&where%5Bid%5D="+str(my_subtitle.id)+" \n\n"+
        "Video-Adresse: "+video_link+"\n"+
        "Konvertierungsseite (falls nötig :( ): http://www.3playmedia.com/services-features/free-tools/captions-format-converter/ \n\n" +
        "Screencast vom ganzen Prozess: https://www.youtube.com/watch?v=bydO0-fQyqQ \n\n" +
        "1. File aus dem Anhang dieser E-Mail runter laden\n" +
        "2. In Youtube auf der Seite des Videos einloggen. Dazu oben rechts 'Anmelden' anklicken und einloggen und dann media.ccc.de als Identität auswählen.\n" +
        "3. Die Sprache des Videos einstellen. Das sollte 'German' oder 'English' sein und nichts anderes.\n" +
        "4. Unter dem Video auf 'cc' klicken.\n" +
        "5. Die angezeigten von YT erstellten Untertitel anklicken.\n" +
        "6. Im dann aufgehenden Bearbeiten-Fenster oben rechts 'Actions' 'Unpublish' auswählen.\n" +
        "7. Nochmal 'Actions' anklicken und dieses mal 'Discard edits' auswählen und 'Discard edits' bestätigen.\n" +
        "8. 'Add new subtitle or CC' anklicken und Sprache auswählen.\n" +
        "9. 'Upload a file' auswählen und als 'Transcript' das *.transcript-File was im Anhang dieser Mail war hochladen.\n" +
        "10. Im erscheinenden Editor unten rechts auf 'Set timings' klicken\n" +
        "11. Warten bis kein 'setting timings' mehr angezeigt wird. Dann anklicken. (Kann durchaus 10 Minuten dauern)\n" +
        "12. Oben rechts 'Actions' -> 'Download'anklicken und das *.sbv-File speichern.\n" +
        "13. Oben rechts 'Actions' -> 'discard edits' auswählen und bestätigen. Jetzt sollten alle Untertitel gelöscht sein.\n" +
        "14. Die entsprechende Seite auf Amara öffnen und sich bei amara einloggen. Links auf 'Upload them directly' klicken.\n" +
        "15. Sprache auswählen, 'None direct from Video' so stehen lassen, das File aussuchen und unbedingt den Haken bei 'The subtitle file is 100% complete' entfernen.\n" +
        "16. Auf c3subtitles.ext.selfnet.de per ssh einloggen.\n" +
        "17. 'cd /opt/subtitleStatus && source virtualEnv/bin/activate' auf der Shell ausführen.\n"+
        "18. 'python reset_subtitle_from_blocked_to_quality_control.py " + str(my_subtitle.id) + "' ausführen.\n" +
        "19. Auf www.c3subtitles.de nachsehen ob es funktioniert hat und auf https://twitter.com/c3srt_releases nachsehen ob ein Tweet kam.", "plain")
    msg.attach(text)
    msg["Subject"] = "Transcript needs your attention: "+str(my_subtitle.talk.frab_id_talk)+' "'+my_subtitle.talk.title+'" Talk-ID: ' + str(my_subtitle.talk.id) + " Subt-ID: " + str(my_subtitle.id)
    msg["From"] = FROM
    msg["To"] = TO

    try:
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
        p.communicate(msg.as_string())
        return True
    except:
        return False

def do_toot(mastodon_client, text, visibility=None, in_reply_to_id=None,quote_id=None):
    return mastodon_client.status_post(status=text, visibility=visibility, in_reply_to_id=in_reply_to_id, quote_id=quote_id)

# For emojis look here: https://www.webfx.com/tools/emoji-cheat-sheet/
def message_to_rocket_chat_with_webhook(webhook, data = {"text":"", "alias": "", "emoji": ""}):
    headers = {'Content-Type': 'application/json',}
    return requests.post(webhook, headers=headers, data=json.dumps(data))

def notify_transcript_available(my_talk):
    # Via Mastodon Progress Account
    do_toot(mastodon_c3srt_progress, create_text_for_transcript_is_now_available(my_talk, text_format = "Mastodon"), visibility="unlisted")
    
    # Via Rocket Chat #subtitles-notifications
    message_to_rocket_chat_with_webhook(cred.ROCKET_CHAT_WEBHOOK_SUBTITLES_NOTIFICATIONS, data = {"text": create_text_for_transcript_is_now_available(my_talk, text_format = "Text"), "alias": "C3Subtitles Bot", "emoji": ":point_right:"})

def notify_transcript_needs_timing(my_subtitle):
    # Via Rocket Chat INTERN
    message_to_rocket_chat_with_webhook(cred.ROCKET_CHAT_WEBHOOK_SUBTITLES_INTERN, data = {"text": create_text_for_subtitle_needs_timing(my_subtitle), "alias": "C3Subtitles Bot", "emoji": ":point_right:"})

def notify_subtitle_ready_for_quality_control(my_subtitle):
    # Via Mastodon Progress Account
    do_toot(mastodon_c3srt_progress, create_text_for_subtitle_ready_for_quality_control(my_subtitle, text_format = "Mastodon"), visibility="unlisted")
    
    # Via Rocket Chat #subtitles-notifications
    message_to_rocket_chat_with_webhook(cred.ROCKET_CHAT_WEBHOOK_SUBTITLES_NOTIFICATIONS, data = {"text": create_text_for_subtitle_ready_for_quality_control(my_subtitle, text_format = "Text"), "alias": "C3Subtitles Bot", "emoji": ":point_right:"})

def notify_subtitle_released(my_subtitle):
    # Via Mastodon Progress Account
    do_toot(mastodon_c3srt_releasing, create_text_for_subtitle_is_released(my_subtitle, text_format = "Mastodon"), visibility="unlisted")
    
    # Via Rocket Chat #subtitles-notifications
    message_to_rocket_chat_with_webhook(cred.ROCKET_CHAT_WEBHOOK_SUBTITLES_NOTIFICATIONS, data = {"text": create_text_for_subtitle_is_released(my_subtitle, text_format = "Text"), "alias": "C3Subtitles Bot", "emoji": ":thumbsup:"})
