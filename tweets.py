#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script helps creating Tweets for released subtitles ans sending them
# No Flags will be reset!
#==============================================================================

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Subtitle, Talk, Event, Language

import twitter as tw
import credentials as cred

# A subtitle on media has been released or updated
def create_tweet_for_media(subtitle_id):
    # Check if there really is a subtitle available with this Id:
    try:
        my_subtitle = Subtitle.objects.get(id = subtitle_id)
    except:
        return(None)
    #  Stop if the subtitle is not completed
    if not my_subtitle.complete:
        return(None)
    
    # Get associated Data from the database
    try:
        my_talk = Talk.objects.get(id = my_subtitle.talk_id)
        my_language = Language.objects.get(id = my_subtitle.language_id)
        my_event = Event.objects.get(id = my_talk.event_id)
    except:
        return(None)
        
    # Workaround for Klingon :D
    if my_language.id = 289
        my_language.language_en = "Original"
    string = my_language.language_en + " #subtitles released for "
    name_of_talk = my_talk.title
    hashtag = my_event.hashtag
    link = "https://cdn.media.ccc.de" + my_event.ftp_startfolder[3:]
    # Länge des Tweets setzt sich zusammen aus den Strings und 23 Zeichen für den Link
    while len(string) + 4 + len(name_of_talk) + 3 + 23 + len(hashtag) + 1 > 140:
        name_of_talk = name_of_talk[:-2]
        name_of_talk = name_of_talk + "…"
    
    my_tweet = string + '"' + name_of_talk + '" on: ' + link + " " + hashtag
    #print (my_tweet)
    return my_tweet
    
# A subtitle on YT has been released or updated    
def create_tweet_for_YT(subtitle_id):
    # Check if there really is a subtitle available with this Id:
    try:
        my_subtitle = Subtitle.objects.get(id = subtitle_id)
    except:
        return(None)
    #  Stop if the subtitle is not completed
    if not my_subtitle.complete:
        return(None)
    
    # Get associated Data from the database
    try:
        my_talk = Talk.objects.get(id = my_subtitle.talk_id)
        my_language = Language.objects.get(id = my_subtitle.language_id)
        my_event = Event.objects.get(id = my_talk.event_id)
    except:
        return(None)
        
    # Workaround for Klingon :D
    if my_language.id = 289
        my_language.language_en = "Original"
    string = my_language.language_en + " #subtitles released for "
    name_of_talk = my_talk.title
    hashtag = my_event.hashtag
    link = "https://youtube.com/user/mediacccde"
    # Länge des Tweets setzt sich zusammen aus den Strings und 23 Zeichen für den Link
    while len(string) + 4 + len(name_of_talk) + 3 + 23 + len(hashtag) + 1 > 140:
        name_of_talk = name_of_talk[:-2]
        name_of_talk = name_of_talk + "…"
    
    my_tweet = string + '"' + name_of_talk + '" on: ' + link + " " + hashtag
    #print (my_tweet)
    return my_tweet

# Pure tweeting
def do_tweet(tweet_content = "Something!"):
    if tweet_content == None:
        return False
    my_twitter = tw.Twitter( auth = tw.OAuth(cred.TW_C3R_ACCESS_TOKEN,
        cred.TW_C3R_ACCESS_TOKEN_SECRET,
        cred.TW_C3R_API_KEY,
        cred.TW_C3R_API_SECRET))
    try:
        my_twitter.statuses.update(status = tweet_content)
        return True
    except tw.TwitterHTTPError as e:
        return False

# Tweet only media.ccc.de releases/updates
def tweet_subtitles_update_media(id):
    return do_tweet(create_tweet_for_media(id))

# Tweet only YT releases/updates
def tweet_subtitles_update_YT(id):
    return do_tweet(create_tweet_for_YT(id))
 
# Tweet for YT and media updates/releases
def tweet_subtitles_update(id):
    ret_1 = tweet_subtitles_update_media(id)
    ret_2 = tweet_subtitles_update_YT(id)
    if ret_1 == ret_2 == True:
        return True
    else:
        return False