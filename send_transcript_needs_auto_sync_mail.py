#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts checks for the flag "needs_automatic_syncing" in the database
# If a subtitle has that flag it sends an e-mail to people who can do the
# autotiming of the transcript on Youtube
# Afterwards it resets the flag in the database
# When the timed *.sbv from youtube is back in amara the script:
# "reset_subtitle_form_blcoked_to_quality_control.py" should be run
#==============================================================================

import os
import sys
import urllib
import re

# E-Mail-Stuff
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
#from email.mime.image import MIMEImage
from email import encoders

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Language, Subtitle

import credentials as cred

# Search for subtitles with set flag "needs_automatic_syncing"
my_subtitles = Subtitle.objects.filter(needs_automatic_syncing = True)

FROM = "localhost@subtitles.ber.c3voc.de"
TO = cred.E_MAIL_TO_FOR_TRANSCRIPTS_TIMING
TEXT = []
TEXT.append("These Subtitle-Files need your attention: ")

for any in my_subtitles:
    language = any.language.lang_amara_short
    amara_key = any.talk.amara_key
    url = "https://www.amara.org/api2/partners/videos/"+amara_key+"/languages/"+str(language)+"/subtitles/?format=txt"
    
    # Building the email
    msg = MIMEMultipart()
    
    # Fix für keinen Video-Link in der DB
    video_link = any.talk.link_to_video_file
    if video_link == "":
        video_link = "https://www.youtube.com/watch?v=" + any.talk.youtube_key
    
    # Build text for email with important Links
    text = MIMEText("Talk: "+any.talk.title+" \n"+
        "Talk-ID: "+str(any.talk.id)+"\n"+
        "Subtitle-ID: "+str(any.id)+"\n"+
        "Subtitle-Sprache: " + language + "\n" +
        "Text-File auf Amara: " + str(url) + "\n\n"+
        "Adminer-Adresse: http://adminer.c3subtitles.de/?pgsql=&db=subtitlestatus&ns=public&edit=www_subtitle&where%5Bid%5D="+str(any.id)+" \n\n"+
        "Video-Adresse: "+video_link+"\n"+
        "Amara-Adresse: "+"www.amara.org/videos/"+any.talk.amara_key+"/ \n" +
        "Talk-Adresse bei uns: https://c3subtitles.de/talk/" + str(any.talk.id) + "\n" +
        "Konvertierungsseite (falls nötig :( ): http://www.3playmedia.com/services-features/free-tools/captions-format-converter/ \n\n" +
        "Screencast vom ganzen Prozess: https://www.youtube.com/watch?v=bydO0-fQyqQ \n\n" +
        "1. txt-File von Amara herunter laden\n" +
        "2. In Youtube auf der Seite des Videos einloggen. Dazu oben rechts 'Anmelden' anklicken und einloggen und dann media.ccc.de als Identität auswählen.\n" +
        "3. Die Sprache des Videos einstellen. Das sollte 'German' oder 'English' sein und nichts anderes.\n" +
        "4. Unter dem Video auf 'cc' klicken.\n" +
        "5. Die angezeigten von YT erstellten Untertitel anklicken.\n" +
        "6. Im dann aufgehenden Bearbeiten-Fenster oben rechts 'Actions' 'Unpublish' auswählen.\n" +
        "7. Nochmal 'Actions' anklicken und dieses mal 'Discard edits' auswählen und 'Discard edits' bestätigen.\n" +
        "8. 'Add new subtitle or CC' anklicken und Sprache auswählen.\n" +
        "9. 'Upload a file' auswählen und als 'Transcript' das txt-File von Amara hochladen.\n" +
        "10. Im erscheinenden Editor unten rechts auf 'Set timings' klicken\n" +
        "11. Warten bis kein 'setting timings' mehr angezeigt wird. Dann anklicken. (Kann durchaus 10 Minuten dauern)\n" +
        "12. Oben rechts 'Actions' -> 'Download'anklicken und das *.sbv-File speichern.\n" +
        "13. Oben rechts 'Actions' -> 'discard edits' auswählen und bestätigen. Jetzt sollten alle Untertitel gelöscht sein.\n" +
        "14. Die entsprechende Seite auf Amara öffnen und sich bei amara einloggen. Links auf 'Upload them directly' klicken.\n" +
        "15. Sprache auswählen, 'None direct from Video' so stehen lassen, das File aussuchen und unbedingt den Haken bei 'The subtitle file is 100% complete' entfernen.\n" +
        "16. Auf subtitles.ber.c3voc.de per ssh einloggen.\n" +
        "17. 'cd /opt/subtitleStatus && source virtualEnv/bin/activate' auf der Shell ausführen.\n"+
        "18. 'python reset_subtitle_from_blocked_to_quality_control.py " + str(any.id) + "' ausführen.\n" +
        "19. Auf subtitles.media.ccc.de nachsehen ob es funktioniert hat und auf https://twitter.com/c3srt_releases nachsehen ob ein Tweet kam.", "plain")
    msg.attach(text)
    msg["Subject"] = "Transcript needs your attention: "+str(any.talk.frab_id_talk)+' "'+any.talk.title+'"'
    msg["From"] = FROM
    msg["To"] = TO
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    
    # Reset Flag
    any.needs_automatic_syncing = False
    any.save()
    
    