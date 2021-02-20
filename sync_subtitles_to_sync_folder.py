#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts checks for the flag "needs_sync_to_sync_folder" and 
# "needs_removal_from_sync_folder"
#
# It uses the class functions sync_subtitle_to_sync_folder and
# remove_subtitle_from_sync_folder.
#
# In the case that the "needs_removal_from_sync_flag" flag was set, it checks
# for the file in the folders and removes them.
#
# Afterwards it sends a log via email and resets the flags in the database
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

from www.models import Talk, Language, Subtitle, Event
import credentials as cred

# Stuff for the e-mail
FROM = cred.E_MAIL_FROM
TO = cred.E_MAIL_TO
TEXT = []

email_text_added_subtitles = "Added subtitle files:\n"
email_text_removed_subtitles = "Removed subtitle files:\n"
email_text_added_draft_subtitles = "Added subtitle draft files:\n"
email_text_removed_draft_subtitles = "Removed subtitle draft files:\n"
# Get all subtitles with flag "needs_sync_to_sync_folder"
my_subtitles = Subtitle.objects.filter(needs_sync_to_sync_folder = True)

#DEBUG
print("Nach DB Abfrage für sync")

# Copy the file to the sync folder
for s in my_subtitles:
    print(s.id)
    s.sync_subtitle_to_sync_folder()
    print(s.id)
    # Add text to email body
    email_text_added_subtitles += s.talk.event.subfolder_in_sync_folder + "/" + s.get_filename_srt() + "\n"
#DEBUG
print("Nach Sync")

# Get all subtitles with flag "needs_removal_from_sync_folder"
my_subtitles = Subtitle.objects.filter(needs_removal_from_sync_folder = True).select_related("talk")
#DEBUG
print("Nach DB Abfrage für removal")

# Copy the file to the sync folder
for s in my_subtitles:
    s.remove_subtitle_from_sync_folder()

    # Add text to email body
    email_text_removed_subtitles += s.talk.event.subfolder_in_sync_folder + "/" + s.get_filename_srt() + "\n"

# Get all subtitles with flag "draft_needs_sync_to_sync_folder"
my_subtitles = Subtitle.objects.filter(draft_needs_sync_to_sync_folder = True).select_related("talk")

# Syncing the draft-files
my_subtitles = Subtitle.objects.filter(draft_needs_sync_to_sync_folder = True).select_related("talk")
for s in my_subtitles:
    s.sync_subtitle_draft_to_sync_folder()
    
    # Add text to email body
    email_text_added_draft_subtitles += s.talk.event.subfolder_in_sync_folder + "/" + s.get_filename_srt(draft=True) + "\n"

# Get all subtitles with flag "draft_needs_removal_from_sync_folder"
my_subtitles = Subtitle.objects.filter(draft_needs_removal_from_sync_folder = True).select_related("talk")

# Removing the draft-files
my_subtitles = Subtitle.objects.filter(draft_needs_removal_from_sync_folder = True).select_related("talk")
for s in my_subtitles:
    s.remove_subtitle_from_sync_folder()

    # Add text to email body
    email_text_removed_draft_subtitles += s.talk.event.subfolder_in_sync_folder + "/" + s.get_filename_srt(draft=True) + "\n"


# Building the email
msg = MIMEMultipart()
msg["Subject"] = "Synced or removed srt files from sync folder"
msg["From"] = FROM
msg["To"] = TO
# Only send an email if something has changed
if email_text_added_subtitles != "Added subtitle files:\n" or email_text_removed_subtitles != "Removed subtitle files:\n":
    text = MIMEText(email_text_added_subtitles+"\n\n"+email_text_removed_subtitles + "\n\n" + email_text_added_draft_subtitles + "\n\n"+ email_text_removed_draft_subtitles, "plain")
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

else: 
    #print("Nothing done!")
    sys.exit(0)
