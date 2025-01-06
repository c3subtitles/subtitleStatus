#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# DEPRECATED this moved into class functions
# the cronjob is done via notifications_cronjob.py
#
# This scripts checks for the flag "notify_subtitle_needs_timing" in the database
# If a subtitle has that flag it sends an e-mail to people who can do the
# autotiming of the transcript on Youtube
# Afterwards it resets the flag in the database
# When the timed *.sbv from youtube is back in amara the script:
# "reset_subtitle_form_blocked_to_quality_control.py" should be run
#==============================================================================

import os
import sys
import urllib
import urllib.request
import re

# E-Mail-Stuff
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
#from email.mime.image import MIMEImage
from email import encoders
from subprocess import Popen, PIPE

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Language, Subtitle

import credentials as cred

# Search for subtitles with set flag "notify_subtitle_needs_timing"
my_subtitles = Subtitle.objects.filter(notify_subtitle_needs_timing = True)
#print(my_subtitles.count())

FROM = "subtitles@c3subtitles.ext.selfnet.de"
TO = cred.E_MAIL_TO_FOR_TRANSCRIPTS_TIMING
TEXT = []
TEXT.append("These Subtitle-Files need your attention: ")

for any in my_subtitles:
    print(any.id)
    language = any.language.lang_amara_short
    amara_key = any.talk.amara_key
    #url = "https://www.amara.org/api2/partners/videos/"+amara_key+"/languages/"+str(language)+"/subtitles/?format=txt"
    slug = any.talk.slug
    url = "https://amara.org/api2/partners/videos/"+amara_key+"/languages/"+str(language)+"/subtitles/?format=srt"

    # Building the email
    msg = MIMEMultipart()

    # Fix für keinen Video-Link in der DB
    video_link = any.talk.link_to_video_file

    # Build text for email with important Links
    text = MIMEText("Talk: "+any.talk.title+" \n"+
        "Talk-ID: "+str(any.talk.id)+"\n"+
        "Subtitle-ID: "+str(any.id)+"\n"+
        "Subtitle-Sprache: " + language + "\n\n" +
        "Adminer-Adresse: http://adminer.c3subtitles.de/?pgsql=&db=subtitlestatus&ns=public&edit=www_subtitle&where%5Bid%5D="+str(any.id)+" \n\n"+
        "Video-Adresse: "+video_link+"\n"+
        "YouTube-Adresse im C3Subtitles YT-Account: https://www.youtube.com/watch?v=" + any.talk.c3subtitles_youtube_key + "\n" +
        "YouTube direkte Untertitel-Adresse: https://studio.youtube.com/video/" + any.talk.c3subtitles_youtube_key +"/translations\n" +
        "Amara-Adresse: "+"https://amara.org/videos/"+any.talk.amara_key+"/ \n" +
        "Talk-Adresse bei uns: https://c3subtitles.de/talk/" + str(any.talk.id) + "\n" +
        "Direkte Admin-Subtitle-Adresse: https://c3subtitles.de/admin/www/subtitle/" + str(any.id) + "\n" +
        "Admin-Subtitle-Adresse: https://c3subtitles.de/admin/www/subtitle/?q=" + str(any.id) + "\n" +
        "Direkte Transforms-Adresse: https://c3subtitles.de/workflow/transforms/" + str(any.id) + "/\n" +
        "Admin-Talk-Adresse: https://c3subtitles.de/admin/www/talk/" + str(any.talk.id) + "\n" +
        "Pad writable link: " + any.talk.link_to_writable_pad + "\n" +
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
        "18. 'python reset_subtitle_from_blocked_to_quality_control.py " + str(any.id) + "' ausführen.\n" +
        "19. Auf www.c3subtitles.de nachsehen ob es funktioniert hat und auf https://chaos.social/@c3srt_releases nachsehen ob ein Toot kam.", "plain")
    msg.attach(text)
    msg["Subject"] = "Transcript needs your attention: "+str(any.talk.frab_id_talk)+' "'+any.talk.title+'"'
    msg["From"] = FROM
    msg["To"] = TO

    """
    # Creating the attachment - not necessary anymore
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    file_content = response.read()
    # Convert from bytes object to string object
    file_content = str(file_content,encoding = "UTF-8")
    #print(file_content)
    # Split in single lines:
    text_content = file_content.splitlines()
    #print(text_content)
    transcript = []
    # Ignore first two lines and check lines afterwards
    transcript.append(text_content[2]+"\n")
    if len(text_content) <= 3:
        i = 4
    elif len(text_content) < 5:
        i = 2
    elif text_content[3] == "":
        i = 3
    elif text_content[4] == "":
        i = 4
    elif text_content[5] == "":
        i = 5


    # Check rest of whole file
    while i < len(text_content):
        # If line is empty jump two down
        if(text_content[i] == ""):
            transcript.append("\n")
            i += 3
        # If line ist not empty save to future output
        else:
            transcript.append(text_content[i]+"\n")
            i += 1

    filename = slug+"."+str(language)+".transcript"
    folder = "./downloads/"
    print(filename)

    # Save File in ./downloads
    file = open(folder+filename,mode = "w",encoding = "utf-8")
    for line in transcript:
        line = re.sub("<i>", "*", line)
        line = re.sub("</i>", "*", line)
        line = re.sub("&amp;", "&", line)
        line = re.sub("&gt;", ">", line)
        file.write(line)
    file.close()

    filename = folder+filename
    print(filename)

    # Build attachment File for email an attach
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(open(filename, 'rb').read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment',filename=os.path.split(filename)[1])
    msg.attach(attachment)
    """

    try:
        p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
        p.communicate(msg.as_string())
        print("Mail send")
    except:
        print("Mail Exception")
        sys.exit(1)


    # old
    #s = smtplib.SMTP('localhost')
    #s.send_message(msg)
    #s.quit()

    # Reset Flag
    any.refresh_from_db()
    any.notify_subtitle_needs_timing = False
    any.save()

sys.exit(0)
