#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# amara_api_helper.py
# This file includes helper functions for the amara api
# It is mainly used in models.py 
#
#==============================================================================

import json
import requests
from .lock import *
import time
import credentials as cred

amara_api_call_sleep_short = 0.1
amara_api_call_sleep_long = 0.8

basis_url =  "https://amara.org/api/videos/"

# Get all URLs currently stored in amara for a specific video
# Additional info like the id and if the url is a primary or was the original
# is also read and returned
def get_uploaded_urls(talk):
    api_url = basis_url + talk.amara_key + "/urls/"
    if talk.amara_key == "":
        return {}
    # Get the id of the url and make it primary afterwards
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep_long)
        result = requests.get(api_url, headers = cred.AMARA_HEADER)
    results_json = json.loads(result.content)
    links_on_amara = {}
    for any in results_json["objects"]:
        this_url = any['url']
        links_on_amara[this_url] = {}
        links_on_amara[this_url]['id'] = any['id']
        links_on_amara[this_url]['primary'] = any['primary']
        links_on_amara[this_url]['original'] = any['original']
    return links_on_amara


# If a URL is already uploaded you can't upload the url a second time with primary = True
# You have to get the id of the URL and mark it as primary
def make_uploaded_url_primary(url, talk):
    api_url = basis_url + talk.amara_key + "/urls/"
    if talk.amara_key == "":
        return None
    # Get the id of the url and make it primary afterwards
    links_on_amara = get_uploaded_urls(talk=talk)
    if url in links_on_amara:
        pass
    else:
        return None
    api_url = api_url + str(links_on_amara[url]['id']) + "/"
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep_long)
        result = requests.put(api_url, headers = cred.AMARA_HEADER, data=json.dumps({'primary':True}))
    if str(result) == "<Response [200]>":
        return True
    else:
        return False


# Remove an URL from amara
# To do this, you need the ID of the URL
# Return None if the url is not connected with that amara link
# Return False if it is a primary url which can not be removed
def remove_url_from_amara(url, talk):
    # Get all urls on amara and their ID and put it in a dictionary
    # Check if the url which is supposed to get removed is in the dictionary
    links_on_amara = get_uploaded_urls(talk=talk)

    # If the url is not connected with the talk stop trying to remove it
    # and return None
    if url in links_on_amara:
        pass
    else: 
        return None

    # Removing of a primary link is not possible
    if links_on_amara[url]['primary'] == True:
        return False
    api_url = basis_url + talk.amara_key + "/urls/" + str(links_on_amara[url]['id']) + "/"
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep_long)
        result = requests.delete(api_url, headers = cred.AMARA_HEADER)
    if str(result) == "<Response [204]>" :
        return True
    else:
        return False


# Check if a url is already on amara
# If the url is on amara return the amara_key
def check_if_url_on_amara(url):
    api_url = basis_url + "?video_url=" + url
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep_long)
        result = requests.get(api_url, headers = cred.AMARA_HEADER)
    result_json = json.loads(result.content)
    # If the url is not on amara, no data returned
    if len(result_json["objects"]) == 0:
        return False
    else:
        amara_key = result_json["objects"][0]["id"]
        return amara_key


# Check if a specific url is already on amara
# As additional check, check if the url is up and primary
def check_if_url_is_on_amara_with_a_known_talk(url, talk, also_check_if_primary = False):
    # Return None if the talk does not yet have an amara key
    if talk.amara_key == "":
        return None
    # Return False if the url is not on amara in general
    if check_if_url_on_amara(url) == False:
        return False

    # Get all urls from amara, compare to the ones you have and if it is primary
    api_url = basis_url + talk.amara_key + "/urls/"
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep_long)
        result = requests.get(api_url, headers = cred.AMARA_HEADER)
    results_dict = result.json()
    links_on_amara = {}
    for any in results_dict["objects"]:
        links_on_amara[any['url']] = any['primary']
    if url in links_on_amara:
        if also_check_if_primary:
            if links_on_amara[url] == True:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


# Read which links are stored in amara for a specific video
# Download these urls and store them in c3subtitles
def read_links_from_amara(talk, do_save = True):
    if talk.amara_key == "":
        return None
    links_on_amara = get_uploaded_urls(talk)
    talk.primary_amara_video_link = ""
    talk.additional_amara_video_links = ""
    for any_link in links_on_amara.keys():
        if links_on_amara[any_link]['primary']:
            talk.primary_amara_video_link = any_link
        else:
            talk.additional_amara_video_links = talk.additional_amara_video_links + " " + any_link
    talk.additional_amara_video_links = talk.additional_amara_video_links[1:]
    if do_save:
        talk.save()
    return [talk.primary_amara_video_link, talk.additional_amara_video_links]


# Create the amara_key with the primary url and store it in the db
def create_and_store_amara_key(talk):
    # Stop if there is no primary video link
    if talk.primary_amara_video_link == "":
        return None
    url = talk.primary_amara_video_link
    result = check_if_url_on_amara(url)
    if result != False:
        talk.amara_key = result
        talk.save()
        return talk.amara_key
    basis_url = "https://amara.org/api/videos/"
    # If the talk does not have an amara key yet, create one and store it
    if talk.amara_key == "":
        parameters = {"video_url": url,
            "primary_audio_language_code": talk.orig_language.lang_amara_short}
        with advisory_lock(amara_api_lock) as acquired:
            time.sleep(amara_api_call_sleep_long)
            r = requests.post(basis_url, headers = cred.AMARA_HEADER, data = json.dumps(parameters))
        return_content = json.loads(r.content)
        talk.amara_key = return_content["id"]
        talk.save()
        return talk.amara_key


# Add the additional links to an amara key of a talk
def add_additional_links_to_amara(talk):
    api_url = basis_url + talk.amara_key + "/urls/"
    sec_urls = talk.additional_amara_video_links.split(" ")
    for any_url in sec_urls:
        parameters = {"url": any_url,
            "primary": False}
        with advisory_lock(amara_api_lock) as acquired:
            time.sleep(amara_api_call_sleep_long)
            r = requests.post(api_url, headers = cred.AMARA_HEADER, data = json.dumps(parameters))
    return True


# Compare which links are in the database and which links are in amara
# Mirror the status in c3subtitles to amara, not the opposite
def update_amara_urls(talk):
    # First make sure all links which should be on amara are up
    # and a amara key actually exists
    result = create_and_store_amara_key(talk)
    # If there is no primary video link, stop here
    if result == None:
        return None
    # Make sure the primary links is actually the primary link
    make_uploaded_url_primary(talk.primary_amara_video_link, talk)

    # Make sure all additional links are uploaded
    add_additional_links_to_amara(talk)

    # Remove links which are on amara but are not in the database any more
    # Get the links which are uploaded
    # Compare to links 
    uploaded_links = get_uploaded_urls(talk)
    links_in_db = {}
    # Create the links in the database dictionary
    for any_link in talk.additional_amara_video_links.split(" "):
        links_in_db[any_link] = 0
    # Check if a link from amara is in the db, else remove it
    for u_link in uploaded_links:
        if u_link in links_in_db:
            pass
        else:
            remove_url_from_amara(u_link, talk)