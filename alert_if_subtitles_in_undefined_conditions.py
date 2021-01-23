#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts checks for several conditions in the database which e.g.
# occur it a user did not click the "finished transcribing" button or if
# the subtitle is here marked as complete but not at amara.
#
# This script collects all these special cases and sends an email with
# cases in which something seems to be off.
#
# This script should run as cronjob e.g. once per hour
#
#==============================================================================

import os
import sys
import urllib
#import re
#import pysftp
#import shutil

# E-Mail-Stuff
#import smtplib
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

from www.models import Subtitle
from django.db.models import F
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
import credentials as cred

delta = timedelta(hours=1, minutes=2)

# Stuff for the e-mail
FROM = cred.E_MAIL_FROM
TO = cred.E_MAIL_TO
TEXT = []

send_mail = False

def pretty_print_subtitle_dataset(subt):
    return_string = ""
    return_string += "Talk Title: " + subt.talk.title + "\n"
    return_string += "Talk ID: " + str(subt.talk.id) + "\n"
    return_string += "Subt ID: " + str(subt.id) + "\n"
    return_string += "Language: " + subt.language.language_en + "\n"
    return_string += "Orig Lang: " + str(subt.is_original_lang) + "\n"
    return_string += "State: " + str(subt.state.id) + " " + subt.state.state_en + "\n"
    return_string += "Complete: " + str(subt.complete) + "\n"
    return_string += "Video duration: " + subt.talk.video_duration.strftime("%H:%M:%S") + "\n"
    if subt.is_original_lang:
        return_string += "Time transcribed: " + subt.time_processed_transcribing.strftime("%H:%M:%S") + "\n"
        return_string += "Time synced: " + subt.time_processed_syncing.strftime("%H:%M:%S") + "\n"
        return_string += "Time quality checked: " + subt.time_quality_check_done.strftime("%H:%M:%S") + "\n"
    else:
        return_string += "Time translated: " + subt.time_processed_translating.strftime("%H:%M:%S") + "\n"

    return_string += "Link talk c3subtitles: https://www.c3subtitles.de/talk/" + str(subt.talk.id) + "\n"
    return_string += "Link talk in Admin: https://www.c3subtitles.de/admin/www/talk/" + str(subt.talk.id) + "\n"
    return_string += "Link subtitle in Admin: https://www.c3subtitles.de/admin/www/subtitle/" + str(subt.id) + "\n"

    return return_string

e_mail_content = ""

"""
Find all subtitles which are original language (orig_lang = True)
Still in transcribing mode (state_id = 2)
Not complete (complete = False)
The time processed transcribing is exactly the video duration
     talk__video_duration = F('time_quality_check_done')
"""
subtitles_finished_transcribing_not_clicked = Subtitle.objects.all().filter(complete=False, state_id=2, talk__video_duration=F('time_processed_transcribing'), touched__gte=make_aware(datetime.now())-delta)
#print(subtitles_finished_transcribing_not_clicked.count())
if subtitles_finished_transcribing_not_clicked.count() > 0:
    e_mail_content += "orig_lang = True, state_id = 2, time_quality_check_done = video_duration\n"
    e_mail_content += "User probably forgot to click the 'finished transcribing' button:\n"
    for any in subtitles_finished_transcribing_not_clicked:
        e_mail_content += pretty_print_subtitle_dataset(any) + "\n"
    e_mail_content += "\n"


"""
Find all subtitles which appear to be complete but are not actually
complete in amara
This happens in some rare cases when a user first saves and then clicks "publish" in amara without a later change with a new revision
Additional the user clicks on c3subtitles.de on "finished"
"""
subtitles_not_complete_in_amara = Subtitle.objects.all().filter(complete=False,state_id=7, talk__video_duration=F('time_quality_check_done'), touched__gte=make_aware(datetime.now())-delta)
#print(subtitles_not_complete_in_amara.count())
if subtitles_not_complete_in_amara.count() > 0:
    e_mail_content += "complete=False, state_id=7, time_quality_check_done=video_duration\n"
    e_mail_content += "The subtitle looks complete but is not marked as complete in amara, in the db the time is set to the video_duration but no button was pressed:\n"
    for any in subtitles_not_complete_in_amara:
        e_mail_content += pretty_print_subtitle_dataset(any) + "\n"
    e_mail_content += "\n"


"""
Translations which are not complete in amara but appear to be complete on c3subtitles.de
"""
subtitles_translation_not_complete_in_amara = Subtitle.objects.all().filter(state_id=11, complete=False, talk__video_duration=F('time_processed_translating'), touched__gte=make_aware(datetime.now())-delta)
#print(subtitles_translation_not_complete_in_amara.count())
if subtitles_translation_not_complete_in_amara.count() > 0:
    e_mail_content += "complete=False, state_id=11, time_processed_translating=video_duration\n"
    e_mail_content += "Translation is not complete in amara but the user set the time_processed_translating to the video_duration:\n"
    for any in subtitles_translation_not_complete_in_amara:
        e_mail_content += pretty_print_subtitle_dataset(any)
    e_mail_content += "\n"


"""
Orignal language, not complete in amara but appear to complete on c3subtitles.de
"""
subtitles_not_complete_but_user_clicked = Subtitle.objects.all().filter(complete=False, state_id=8, touched__gte=make_aware(datetime.now())-delta)
#print(subtitles_not_complete_but_user_clicked.count())
if subtitles_not_complete_but_user_clicked.count() > 0:
    e_mail_content += "complete=False, state_id=8\n"
    e_mail_content += "The subtitle is not complete in amara but the user clicked the 'job complete' button on c3subtitles:\n"
    for any in subtitles_not_complete_but_user_clicked:
        e_mail_content += pretty_print_subtitle_dataset(any)
    e_mail_content += "\n"


"""
Translation which is not complete in amara but appears to be complete on c3subtitles.de
"""
subtitles_translation_not_complete_but_user_clicked = Subtitle.objects.all().filter(state_id=12, complete=False, touched__gte=make_aware(datetime.now())-delta)
#print(subtitles_translation_not_complete_but_user_clicked.count())
if subtitles_translation_not_complete_but_user_clicked.count() > 0:
    e_mail_content += "complete=False, state_id=12\n"
    e_mail_content += "The translation is not complete in amara but the user clicked the 'translation finished' button:\n"
    for any in subtitles_translation_not_complete_but_user_clicked:
        e_mail_content += pretty_print_subtitle_dataset(any)
    e_mail_content += "\n"


# Stop here if no suspicious dataset was found
if e_mail_content == "":
    #print("Nothing to do")
    sys.exit(0)

#print(e_mail_content)

# Building the email
msg = MIMEMultipart()
msg["Subject"] = "Suspicious datasets which need a second look"
msg["From"] = FROM
msg["To"] = TO

text = MIMEText(e_mail_content, "plain")
msg.attach(text)
try:
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
    p.communicate(msg.as_string())
    sys.exit(0)
except:
    sys.exit(1)
    #s = smtplib.SMTP('mail.selfnet.de')
    #try:
    #    s.send_message(msg)
    #except:
    #    sys.exit(1)
    #s.quit()


    #print("Nothing done!")
sys.exit(0)
