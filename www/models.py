# -*- coding: utf-8 -*-

from time import sleep
from datetime import datetime, time, timezone, timedelta
from django.db import models, transaction
from django.db.models import Sum, Q
from django.urls import reverse
from django.core.validators import URLValidator
from django.utils.deconstruct import deconstructible
from django import forms
from django.db import transaction
from django.utils.timezone import make_aware
# TODO: figure out what needs to be imported here. Still better than
# `import *`, which will silently overwrite, e.g., `time`, and thus
# break everything down below.
from .statistics_helper import calculate_seconds_from_time, calculate_time_delta, calculate_per_minute, calculate_subtitle, prepare_string_for_word_counts, save_word_dict_as_json, read_word_dict_from_json, merge_word_frequencies_dicts, n_most_common_words
from .amara_api_helper import get_uploaded_urls, make_uploaded_url_primary, remove_url_from_amara, check_if_url_on_amara, update_amara_urls, read_links_from_amara, create_and_store_amara_key
from .trint_api_helper import get_trint_transcript_via_api

import json
import requests
import credentials as cred
from .lock import *


# How long should the script wait when it calls the amara api
amara_api_call_sleep = 0.1 # seconds
amara_api_call_sleep_fast_functions = 0.8

@deconstructible
class MaybeURLValidator(URLValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, value):
        if value == '#':
            return

        if value.startswith('#'):
            value = value[1:]

        super().__call__(value)

    def __eq__(self, other):
        return super().__eq__(other)


class MaybeURLFormField(forms.fields.URLField):
    default_validators = [MaybeURLValidator()]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python(self, value):
        if value.startswith('#'):
            return value
        return super().to_python(value)


class MaybeURLField(models.URLField):
    default_validators = [MaybeURLValidator()]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': MaybeURLFormField,
            **kwargs,
            })


def get_amara_header(cred):
    """Return a header suitable for authenticating against the amara API."""
    return {'Content-Type': 'application/json',
            'X-api-username': cred.AMARA_USER,
            'X-api-key': cred.AMARA_API_KEY,
    }


# Basic model which provides a field for the creation and the last change timestamp
class BasisModell(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    touched = models.DateTimeField(auto_now = True)

    class Meta:
        abstract = True


"""
# For every event in which subfolder on the ftp the subtitles are supposed to appear and with which file extensions
class Folders_Extensions(BasisModell):
    subfolder = models.CharField(max_length = 10, default = "", blank = True)
    file_extension = models.CharField(max_length = 10, default = "", blank = True)

    def __str__(self):
        return self.subfolder+","+self.file_extension
"""


# Event and its data
class Event(BasisModell):
    schedule_version = models.CharField(max_length = 250, default = "0.0", blank = True)
    acronym = models.CharField(max_length = 50, default = "", blank = True)
    title = models.CharField(max_length = 100, default = "No title yet", blank = True)
    start = models.DateField(default=make_aware(datetime.min), blank=True)
    end = models.DateField(default=make_aware(datetime.min), blank=True)
    timeslot_duration = models.TimeField(default=time(minute=15), blank=True)
    days = models.PositiveSmallIntegerField(default = 1, blank = True)
#    schedule_xml_link = models.URLField()
    schedule_xml_link = MaybeURLField()
    city = models.CharField(max_length = 30, default = "", blank = True)
    building = models.CharField(max_length = 30, default = "", blank = True)
    #ftp_startfolder = models.CharField(max_length = 100, default = "", blank = True)
    #ftp_subfolders_extensions = models.ManyToManyField(Folders_Extensions, default = None, blank = True)
    hashtag = models.CharField(max_length = 50, default = "", blank = True)
    subfolder_to_find_the_filenames = models.CharField(max_length = 20, default = "", blank = True) # To find the right filenames via regex via frab-id
    speaker_json_link = MaybeURLField(blank = True, default = "")
    speaker_json_version = models.CharField(max_length = 50, default = "0.0", blank = True)
    unlisted = models.BooleanField(default = False, blank = True)
    #cdn_subtitles_root_folder = models.URLField(default = "", blank = True)
    subfolder_in_sync_folder = models.CharField(max_length = 100, default = "", blank = True) # For the rsync to the selfnet mirror, no slashes at the beginning and end
    frab_id_prefix = models.CharField(max_length = 100, default = "", blank = True) # This allows other frab-id offsets of other events to be unique too in the database
    kanboard_public_project_id = models.IntegerField(blank = True, null = True)
    kanboard_private_project_id = models.IntegerField(blank = True, null = True)
    comment = models.TextField(default = "", blank = True, null = True)
    trint_folder_id = models.CharField(max_length = 30, default = "", blank = True)
    lang_subst_json = models.TextField(default='{"en":"eng", "de":"deu"}') # how are the languages displayed in the filenames in the media cdn? needed to find the filenames and video file urls
    webpages_to_find_video_links_and_filenames = models.TextField(default="") # one or several ";" separated links to webpages e.g. from the cdn to find the filenames and video files, first priority first
    endings_to_remove_from_filenames = models.CharField(max_length=100, default='_hd.mp4;_sd.mp4;.mp4')# one or several ";" separated substitutions at the ends of the filenames
    use_all_webpages_urls_to_find_filenames_and_video_urls = models.BooleanField(default = True) # if all urls should be used to find the filenames and video urls or just following the priority

    def isDifferent(id, xmlFile):
        with open("data/eventxml/{}.xml".format(id),'rb') as f:
            savedXML = f.read()
            return savedXML == xmlFile.data

    def get_absolute_url(self):
        return reverse('event', args=[self.acronym])


    # Create Entries in Statistics_Event model for any available combination
    def create_statistics_event_entries(self):
        my_subtitles = Subtitle.objects.filter(is_original_lang = True, talk__event = self)
        my_talks = Talk.objects.filter(event = self)
        for any in my_subtitles:
            this = Statistics_Event.objects.get_or_create(event = self, language = any.language)
            # If new created, than also set the flag for recalculate
            if this[1]:
                this[0].recalculate_statistics = True
                this[0].save()
        for any in my_talks:
            this = Statistics_Event.objects.get_or_create(event = self, language = any.orig_language)
            # If new created, also recalculate
            if this[1]:
                this[0].recalculate_statistics = True
                this[0].save()

    @property
    def page_sub_titles(self):
        return [self.title]

    @property
    def has_statistics(self):
        statistics_this_event = Statistics_Event.objects.filter(event = self)
        if statistics_this_event.count() == 0:
            return False
        else:
            counter_statistics_with_none = 0
            for any in statistics_this_event:
                if any.words == None:
                    counter_statistics_with_none += 1
            if counter_statistics_with_none == statistics_this_event.count():
                return False
            else:
                return True

    @property
    def complete_content_duration(self):
        """ How 'long' is all material we have of an event """
        my_talks = Talk.objects.filter(unlisted = False, event = self)
        sum = 0
        for any in my_talks:
            # Special case for talks who have no specific video_duration yet
            if any.video_duration == "00:00:00":
                sum += calculate_seconds_from_time(any.duration)
            else:
                sum += calculate_seconds_from_time(any.video_duration)
        all_in_seconds = sum
        hours = int(sum //3600)
        sum -= 3600 * hours
        minutes = int(sum // 60)
        sum -= 60* minutes
        seconds = int(sum)
        return [all_in_seconds, hours, minutes, seconds]

    # Save Fahrplan xml file with version in the name into ./www/static/
    def save_fahrplan_xml_file(self):
        import datetime
        if self.schedule_xml_link[0:1] == "#" or self.schedule_xml_link == "":
            return None
        from urllib import request
        from lxml import etree
        response = request.urlopen(self.schedule_xml_link)
        # Read as file
        file_content = response.read()
        file_content = str(file_content,encoding = "UTF-8")
        # Get the version from the xml
        tree = etree.parse(request.urlopen(self.schedule_xml_link))
        fahrplan = tree.getroot()
        i = 0
        while i < len(fahrplan):
            if fahrplan[i].tag == "version":
                fahrplan_version = fahrplan[i].text
                break
            else:
                i+=1
        # Create the filename and save
        folder = "./www/static/fahrplan_files/"
        filename = self.acronym + " fahrplan version " + fahrplan_version + " " + "{:%Y-%m-%d_%H:%M:%S}".format(datetime.datetime.now())
        if len(filename)+4 > 255:
            i = 0
            while len(filename)+4 > 255:
                i+=1
                filename = self.acronym + " fahrplan version " + fahrplan_version[0:(-1*i)] + " " + "{:%Y-%m-%d_%H:%M:%S}".format(datetime.datetime.now())
        filename = filename.replace("/","_")
        file = open(folder + filename + ".xml", mode = "w", encoding = "utf-8")
        file.write(file_content)
        file.close()
        return True

    # Save Speaker json file with version in the name into ./www/static/
    def save_speaker_json_file(self):
        import datetime
        if self.speaker_json_link[0:1] == "#" or self.speaker_json_link == "":
            return None
        from urllib import request
        response = request.urlopen(self.speaker_json_link)
        result = response.read()
        result = result.decode("utf8")
        file_content = result
        result = json.loads(result)
        fahrplan_version = result["schedule_speakers"]["version"]
        folder = "./www/static/fahrplan_files/"
        filename = self.acronym + " speaker version " + fahrplan_version + " " + "{:%Y-%m-%d_%H:%M:%S}".format(datetime.datetime.now())
        filename = filename.replace("/","_")
        file = open(folder + filename + ".json",mode = "w",encoding = "utf-8")
        file.write(file_content)
        file.close()
        return True

    def __str__(self):
        return self.acronym


# Days which belong to an event
class Event_Days(BasisModell):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    index = models.PositiveSmallIntegerField(default = 0)
    date = models.DateField(default=make_aware(datetime.min), blank=True)
    day_start = models.DateTimeField(default=make_aware(datetime.min), blank=True)
    day_end = models.DateTimeField(default=make_aware(datetime.min), blank=True)

    def __str__(self):
        return 'Day {}'.format(self.index) + " - " + self.event.acronym


# "Rooms" in which an event takes place, might also be outside
class Rooms(BasisModell):
    room = models.CharField(max_length = 40, default = "kein Raum")
    building = models.CharField(max_length = 30, default = "")

    def __str__(self):
        return self.room


# Different languages and their "codes" in amara or the name in German end English in full names
class Language(BasisModell):
    language_en = models.CharField(max_length = 40, default = "")
    language_de = models.CharField(max_length = 40, default = "", blank = True)
    #lang_short_2 = models.CharField(max_length = 3, default = "", blank = True)#, unique = True) not really used
    lang_amara_short = models.CharField(max_length = 15, default = "", unique = True)
    lang_short_srt = models.CharField(max_length = 15, default = "", blank = True)
    language_native = models.CharField(max_length = 40, default = "", blank = True)
    amara_order = models.PositiveSmallIntegerField(default = 0, blank = True)
    lang_code_media = models.CharField(max_length = 4, default = "", blank = True) # ISO 639-2 to talk to the media.ccc.de API
    lang_code_iso_639_1 = models.CharField(max_length = 10, default = "", blank = True)

    def __str__(self):
        return self.lang_amara_short

    # Display-Name of the language in english, no "None" or "Klingon".
    @property
    def display_name(self):
        if self.id == 0 or self.id == 289:
            return "Original (mixed)"
        else:
            return self.language_en


# Category of the talk, like "ethics"
class Tracks(BasisModell):
    track = models.CharField(max_length = 100, default = "")

    def __str__(self):
        return self.track


# How the talk is presented, like a workshop or a talk
class Type_of(BasisModell):
    type = models.CharField(max_length = 80, default = "")

    def __str__(self):
        return self.type


# Speaker or Speakers of the Talk
class Speaker(BasisModell):
    frab_id = models.CharField(max_length = 50, default = "-1", blank = True)
    name = models.CharField(max_length = 50, default = "")
    doppelgaenger_of = models.ForeignKey('self', on_delete = models.SET_NULL, blank = True, null = True)
    abstract = models.TextField(default = "", blank = True, null = True)
    description = models.TextField(default = "", blank = True, null = True)

    @property
    def has_statistics(self):
        speakers_statistics = Statistics_Speaker.objects.filter(speaker = self)
        for any in speakers_statistics:
            if any.average_wpm is not None:
                return True
            if any.average_spm is not None:
                return True
        return False

    @property
    def has_links(self):
        speakers_links = Speaker_Links.objects.filter(speaker = self)
        if speakers_links.count() == 0:
            return False
        else:
            return True

    def __str__(self):
        return self.name

    """
    # Probably not needed any more..
    def average_wpm_in_one_talk(self, talk):
        my_statistics = Statistics_Raw_Data.objects.filter(speaker = self, talk = talk)
        words = 0
        time = 0
        for this_statistics in my_statistics:
            if this_statistics.words is not None and this_statistics.time_delta is not None:
                words += this_statistics.words
                time += this_statistics.time_delta
            else:
                return None
        if time == 0:
            return None
        return words * 60.0 / time

    def average_spm_in_one_talk(self, talk):
        my_statistics = Statistics_Raw_Data.objects.filter(speaker = self, talk = talk)
        strokes = 0
        time = 0
        for this_statistics in my_statistics:
            if this_statistics.strokes is not None and this_statistics.time_delta is not None:
                strokes += this_statistics.strokes
                time += this_statistics.time_delta
            else:
                return None
        if time == 0:
            return None
        return strokes * 60.0 / time
    """

    @property
    def page_sub_titles(self):
        return ['Speaker', self.name]


# Links from the Fahrplan
class Speaker_Links(BasisModell):
    speaker = models.ForeignKey(Speaker, blank = True, on_delete=models.PROTECT)
    title = models.CharField(max_length = 300, default = "", blank = True)
    url = models.URLField(blank = True)

# Where is the Transcipt from, autogenerated or handmade
class Transcript (BasisModell):
    creator = models.CharField(max_length = 20, blank = True, null = True) # None, trint, youtube, scribie, handmade ..., default with id=0 is None

    def __str__(self):
        if self.creator is None:
            return '(no transcript)'
        else:
            return self.creator


# Talk with all its data
class Talk(BasisModell):
    frab_id_talk = models.CharField(max_length = 100, default = "-1", blank = True)
    unlisted = models.BooleanField(default=False, blank = True)
    day = models.ForeignKey(Event_Days, default = 1, blank = True, on_delete=models.SET_DEFAULT)
    room = models.ForeignKey(Rooms, default = 15, on_delete=models.PROTECT)
    #link_to_logo = models.URLField(default = "", blank = True)
    date = models.DateTimeField(default=make_aware(datetime.min), blank=True)
    start = models.TimeField(default=time(hour=11), blank=True)
    duration = models.TimeField(default=time(minute=45), blank=True)
    title = models.CharField(max_length = 200, default = "ohne Titel", blank = True)
    subtitle_talk = models.CharField(max_length = 300, default = " ", blank = True) # nicht UT sondern Ergänzung zum Titel
    track = models.ForeignKey(Tracks, default = 40, blank = True, on_delete=models.SET_DEFAULT)
    event = models.ForeignKey(Event, default = 3, blank = True, on_delete=models.SET_DEFAULT)
    type_of = models.ForeignKey(Type_of, default = 9, blank = True, on_delete=models.SET_DEFAULT)
    orig_language = models.ForeignKey(Language, default = 287, blank = True, on_delete=models.SET_DEFAULT)
    abstract = models.TextField(default = "", blank = True)
    description = models.TextField(default = "", blank = True)
    persons = models.ManyToManyField(Speaker, through = "Talk_Persons", default = None, blank = True) #through="Talk_Persons"
    #pad_id = models.CharField(max_length = 30, default = "", blank = True)
    link_to_writable_pad = MaybeURLField(default = "", blank = True)
    link_to_video_file = models.URLField(max_length = 200, default = "", blank = True) # use for trint and upload to c3subtitels YT
    amara_key = models.CharField(max_length = 20, default = "", blank = True)
    c3subtitles_youtube_key = models.CharField(max_length = 20, blank = True)
    video_duration = models.TimeField(default=time(0), blank=True)
    slug = models.SlugField(max_length = 200, default = "", blank = True)
    #youtube_key_t_1 = models.CharField(max_length = 20, blank = True, default = "")
    #youtube_key_t_2 = models.CharField(max_length = 20, blank = True, default = "")
    guid = models.CharField(max_length = 40, blank = True, default = "") # from the Fahrplan
    filename = models.SlugField(max_length = 200, default = "", blank = True) # will be used for a more flexible sftp upload, at the moment only for the subtitles folder in the root-event directory
    time_delta = models.FloatField(blank = True, null = True)   # The duration of the talk in seconds
    words = models.IntegerField(blank = True, null = True)      # Words in the whole subtitles file
    strokes = models.IntegerField(blank = True, null = True)    # Strokes in the whole subtitles file
    average_wpm = models.FloatField(blank = True, null = True)  # Calculated from the words and the time_delta
    average_spm = models.FloatField(blank = True, null = True)  # Calculated from the strokes and the time_delta
    recalculate_talk_statistics = models.BooleanField(default = False)
    speakers_words = models.IntegerField(blank = True, null = True)      # Words in the parts of all speakers
    speakers_strokes = models.IntegerField(blank = True, null = True)    # Strokes in the parts of all speakers
    speakers_time_delta = models.FloatField(blank = True, null = True)   # The duration of the talk in seconds while all speakers speak - the timeslots are in statistics_Raw_Data
    speakers_average_wpm = models.FloatField(blank = True, null = True)  # Calculated from the speakers_words and the speakers_time_delta
    speakers_average_spm = models.FloatField(blank = True, null = True)  # Calculated from the speakers_strokes and the speakers_time_delta
    recalculate_speakers_statistics = models.BooleanField(default = False)
    n_most_frequent_words = models.TextField(default = "{}")    # n most common words as json string
    n_most_frequent_words_speakers = models.TextField(default = "{}")    # n most common words as json string
    has_priority = models.BooleanField(default = False)                 # If the talk has priority because it was requested by someone
    transcript_by = models.ForeignKey(Transcript, default = 0, on_delete=models.SET_DEFAULT)      # Where is the Transcript from? Handmade, None, Youtube, Trint, Scribie...
    amara_activity_last_checked = models.DateTimeField(default=make_aware(datetime.min), blank=True)        # Light check, only amara activity
    amara_update_interval = models.DurationField(default = timedelta(minutes=10), blank = True) # How often is activity checked?
    amara_complete_update_last_checked = models.DateTimeField(default=make_aware(datetime.min), blank=True) # Everything checked, activity and data of every single subtitle
    needs_complete_amara_update = models.BooleanField(default = False)
    next_amara_activity_check = models.DateTimeField(default=make_aware(datetime.min), blank=True)
    internal_comment = models.TextField(default = "", blank = True)
    kanboard_public_task_id = models.IntegerField(blank = True, null = True)
    kanboard_private_task_id = models.IntegerField(blank = True, null = True)
    primary_amara_video_link = models.URLField(default = "", blank = True, max_length = 400) # Video link which is marked as primary on amara
    additional_amara_video_links = models.TextField(default = "", blank = True) # Additional video links separated by whitespace
    trint_transcript_id = models.CharField(max_length = 30, default = "", blank = True)
    notify_transcript_available = models.BooleanField(default = False)

    # Recalculate statistics data over the whole talk
    @transaction.atomic
    def recalculate_whole_talk_statistics(self, force = False):
        # Recalculate statistics data over the whole talk
        # Only if a original subtitle exists which is at least transcribing finished
        my_subtitles = Subtitle.objects.filter(Q(talk = self),
            Q(is_original_lang = True), Q(complete = True) | Q(state_id = 5) |
            Q(state_id = 7) | Q(state_id = 3) | Q(state_id = 6))
        if my_subtitles.count() == 1:
            # In this case, recalculate the time_delta
            if force or self.recalculate_talk_statistics:
                values = calculate_subtitle(self)
                if values is not None:
                    self.time_delta = values["time_delta"]
                    self.words = values["words"]
                    self.strokes = values["strokes"]
                    self.average_wpm = values["average_wpm"]
                    self.average_spm = values["average_spm"]
                    self.recalculate_talk_statistics = False
                    self.save()

                # Save the word frequencies into a json file
                if values["word_frequencies"] is not None and len(values["word_frequencies"]) > 0:
                    save_word_dict_as_json(values["word_frequencies"],"talk_complete", self.id)
                    self.n_most_frequent_words = json.dumps(n_most_common_words(values["word_frequencies"]), ensure_ascii = False)
                    self.save()
                else:
                    self.n_most_frequent_words = "{}"
                    self.save()

                # Set recalculate flags in the Statistics_Event module
                Statistics_Event.objects.filter(event = self.event).update(recalculate_statistics = True)


    # Recalculate Speakers in Talk Statistics-Data
    # If any related data in Statistics_Raw_Data exist!
    @transaction.atomic
    def recalculate_speakers_in_talk_statistics(self, force = False):
        if force or self.recalculate_speakers_statistics:
            # Dictionary for the word freqiencies
            word_freq = {}
            # Check for all Statistics_Raw_Data with this talk no matter which Speaker
            all_datasets = Statistics_Raw_Data.objects.filter(talk = self)
            # If there is no data available, set everything to Null
            if all_datasets.count() == 0:
                self.speakers_words = None
                self.speakers_strokes = None
                self.speakers_time_delta = None
                self.speakers_average_wpm = None
                self.speakers_average_spm = None
                self.recalculate_speakers_statistics = False
                self.save()
            else:
                # Check if any of these datasets first needs a recalculation
                # If so, first recalculate:
                for any_dataset in all_datasets:
                    if any_dataset.recalculate_statistics:
                        any_dataset.recalculate()
                    # Calculate word_frequencies
                    word_freq = merge_word_frequencies_dicts(word_freq, any_dataset.word_frequencies)
                # Sum up all words of any speaker in this talk
                self.speakers_words = all_datasets.aggregate(Sum("words"))["words__sum"]
                # Sum up all strokes of any speaker in this talk
                self.speakers_strokes = all_datasets.aggregate(Sum("strokes"))["strokes__sum"]
                # Sum up time_delta of any speaker in this talk
                self.speakers_time_delta = all_datasets.aggregate(Sum("time_delta"))["time_delta__sum"]
                # Calculate stuff
                self.speakers_average_wpm = calculate_per_minute(self.speakers_words, self.speakers_time_delta)
                self.speakers_average_spm = calculate_per_minute(self.speakers_strokes, self.speakers_time_delta)
                self.recalculate_speakers_statistics = False
                self.save()
            # Save the word frequencies into a json file
            if word_freq is not None and len(word_freq) > 0:
                save_word_dict_as_json(word_freq, "talk_speakers", self.id)
                self.n_most_frequent_words_speakers = json.dumps(n_most_common_words(word_freq), ensure_ascii = False)
                self.save()
            else:
                self.n_most_frequent_words_speakers = "{}"
                self.save()

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        self.recalculate_whole_talk_statistics(force)
        self.recalculate_speakers_in_talk_statistics(force)

    # Reset statistics data related to this talk
    # Is used for a original_subtitle update
    # use hard_reset = True if a subtitle is reset from complete to not complete any more
    @transaction.atomic
    def reset_related_statistics_data(self, hard_reset = False):
        # If hard reset, do reset the values but do not recalculate!
        # Only the Speakers statistics data is not reset here because it would get recalculated anyway
        if hard_reset:
            # Reset everything of the talk and directly related to the talk
            self.average_spm = None
            self.average_wpm = None
            self.strokes = None
            self.words = None
            self.time_delta = None
            self.speakers_average_spm = None
            self.speakers_average_wpm = None
            self.n_most_frequent_words = "{}"
            self.n_most_frequent_words_speakers = "{}"
            Statistics_Raw_Data.objects.filter(talk = self).update(time_delta = None,
                words = None,
                strokes = None)
            Talk_Persons.objects.filter(talk = self).update(average_spm = None,
                average_wpm = None,
                words = None,
                strokes = None,
                time_delta = None,
                n_most_frequent_words = "{}")
        # If no hard_reset only set all recalculate flags
        else:
            Statistics_Raw_Data.objects.filter(talk = self).update(recalculate_statistics = True)
            Talk_Persons.objects.filter(talk = self).update(recalculate_statistics = True)
            self.recalculate_talk_statistics = True
            self.recalculate_speakers_statistics = True
        self.save()

    # Return the n most common words as dict
    @property
    def n_common_words(self):
        return json.loads(self.n_most_frequent_words)

    # Return the n most common words of the speakers as dict
    @property
    def n_common_words_speakers(self):
        return json.loads(self.n_most_frequent_words_speakers)

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("talk_complete", self.id)

    # Return the word_frequencies of speakers as dictionary
    @property
    def word_frequencies_speakers(self):
        return read_word_dict_from_json("talk_speakers", self.id)

    @property
    def needs_automatic_syncing(self):
        return self.subtitle_set.filter(notify_subtitle_needs_timing = True).count() > 0

    # State of the subtitle or its pad
    @property
    def complete(self):
        return self.subtitle_set.filter(complete = False).count() == 0

    @property
    def last_changed_on_amara(self):
        try:
            changed = self.subtitle_set.filter(is_original_lang = True).get().last_changed_on_amara
            for sub in self.subtitle_set.filter(is_original_lang = False):
                if sub.last_changed_on_amara > changed:
                    changed = sub.last_changed_on_amara
            if changed < self.created:
                return None
            else:
                return changed
        # If the talk has no subtitle return the last time it has been touched
        except:
            return None

    def get_absolute_url(self):
        return reverse('talk', args=[str(self.id)])

    @property
    def has_statistics(self):
        """ If there are statistics data available for this talk """
        if self.average_spm is None:
            return False
        elif self.average_spm is None:
            return False
        else:
            return True

    @property
    def has_speakers_statistics(self):
        if self.speakers_average_spm is None:
            return False
        elif self.speakers_average_wpm is None:
            return False
        else:
            return True

    @property
    def language_of_original_subtitle(self):
        this_subtitles = Subtitle.objects.filter(talk = self, is_original_lang = True)
        if this_subtitles.count() == 0:
            return None
        elif this_subtitles.count() == 1:
            return this_subtitles[0].language

    @property
    def has_original_subtitle(self):
        my_subtitles = Subtitle.objects.filter(talk = self, is_original_lang = True)
        if my_subtitles.count() > 0:
            return True
        else:
            return False

    @property
    def has_finished_original_subtitle(self):
        my_subtitles = Subtitle.objects.filter(talk = self, is_original_lang = True, complete = True)
        if my_subtitles.count() > 0:
            return True
        else:
            return False

    @property
    def has_original_subtitle_in_transcript_state(self):
        if self.subtitle_set.filter(is_original_lang = True, state_id = 2).count() >= 1:
            return True
        else:
            return False

    @property
    def has_transcript_by_trint(self):
        if self.transcript_by.id == 3:
            return True
        else:
            return False

    @property
    def has_transcript_by_scribie(self):
        if self.transcript_by.id == 4:
            return True
        else:
            return False

    @property
    def has_transcript_by_youtube(self):
        if self.transcript_by.id == 2:
            return True
        else:
            return False

    @property
    def has_transcript_by_human(self):
        if self.transcript_by.id == 1:
            return True
        else:
            return False

    @property
    def page_sub_titles(self):
        return [self.event.title, self.title]

    @property
    def has_links(self):
        talk_links = Links.objects.filter(talk = self)
        if talk_links.count() == 0:
            return False
        else:
            return True

    # Override delete function
    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Delete related Talk_Persons datasets
        Talk_Persons.objects.filter(talk = self).delete()
        # Delete related Links datasets
        Links.objects.filter(talk = self).delete()
        # Delete related Subtitle datasets
        Subtitle.objects.filter(talk = self).delete()
        # Delete realted Statistics_Raw_Data
        Statistics_Raw_Data.objects.filter(talk = self).delete()

        # Call super delete function
        super(Talk, self).delete(*args, **kwargs)

    # Create a timedelta of the amara_update_interval, for much easier use
    @property
    def calculated_time_delta_for_activities(self):
        return timedelta(seconds = self.amara_update_interval.seconds,
            #minutes = self.amara_update_interval.minutes,
            #hours = self.amara_update_interval.hours,
            microseconds = self.amara_update_interval.microseconds,
            days = self.amara_update_interval.days)

    # Check activity on amara
    @transaction.atomic
    def check_activity_on_amara(self, force = False):
        # Only if the talk has an amara key
        if self.amara_key != "":
            # Take the timestamp for "last executed at" at the beginning of the function
            start_timestamp = datetime.now(timezone.utc)
            # Only proceed if forced or if the time delta for another query has passed
            if force or (start_timestamp > self.next_amara_activity_check):
                import requests
                # Only check for new versions. New urls or other stuff is not interesting
                # Check for changes after the last check
                # If the check is forced, do not care about the last time the activity was checked
                if force:
                    parameters = {'type': 'version-added'}
                else:
                    parameters = {'type': 'version-added',
                        'after': self.amara_activity_last_checked}
                basis_url = "https://amara.org/api/videos/"
                url = basis_url + self.amara_key + "/activity/"
                results = {}
                # Loop as long as not all new activity datasets have been checked
                # Loop only if the talk has an amara_key
                # The json result from amara includes a "next" field which has the url for the next query if not
                # all results came with the first query
                while (url != None) and (url != basis_url + "/activity/"):
                    with advisory_lock(amara_api_lock) as acquired:
                        r = requests.get(url, headers = cred.AMARA_HEADER, params = parameters)
                        sleep(amara_api_call_sleep)
                    #print(r.text)
                    # If amara doesn't reply with a valid json create one.
                    try:
                        activities = json.loads(r.text)
                    except:
                        self.check_amara_video_data()
                        activities = json.loads('{"meta":{"previous":null,"next":null,"offset":0,"limit":20,"total_count":0},"objects":[]}')
                    print(url)
                    url = activities["meta"]["next"]
                    # Get the results for any language separate
                    for any in activities["objects"]:
                        language = any["language"]
                        # Parse the date time string into a datetime object
                        timestamp = datetime.strptime(any["date"], '%Y-%m-%dT%H:%M:%SZ')
                        # Amara Timestamps are all in utc, they just don't know yet, so they need to be force told
                        timestamp = timestamp.replace(tzinfo = timezone.utc)
                        # Add the new key to the dictionary and only at insert set the timestamp
                        results.setdefault(language, timestamp)
                        # Keep the newest timestamp over all api queries
                        if results[language] < timestamp:
                            results[language] = timestamp
                #print(results)
                # check if subtitles are present and need new data..
                for any_language in results.keys():
                    my_subtitles = Subtitle.objects.filter(talk = self, language__lang_amara_short = any_language)
                    # Set flag for big query, this means a subtitle is missing because it was recently new added
                    if my_subtitles.count() == 0:
                        # Set the big update flag
                        self.needs_complete_amara_update = True
                        self.amara_update_interval = timedelta(minutes=5)
                        my_language = Language.objects.get(lang_amara_short = any_language)
                        # Don't create a subtitle here, this will cause subtitles with revision = 0
                        #my_subtitle, created = Subtitle.objects.get_or_create(talk = self, language = my_language, last_changed_on_amara = results[any_language])
                        print("Talk id: ",self.id, " will get a new created subtitle")
                    elif my_subtitles.count() == 1:
                        # Only proceed if the last activity has changed
                        # The copy is a dirty workaround because saving in my_subtitles[0] did not work!
                        my_subtitle = my_subtitles[0]
                        if my_subtitle.last_changed_on_amara < results[any_language]:
                            my_subtitle.last_changed_on_amara = results[any_language]
                            # Set the big update flag
                            self.needs_complete_amara_update = True
                            self.amara_update_interval = timedelta(minutes=5)
                            my_subtitle.save()
                            print("Talk id: ",self.id, "Subtitle id: ", my_subtitle.id, " new last changes:  ", my_subtitle.last_changed_on_amara  )
                    else:
                        print("Something wrong with talk", self.id, self.title)
                # Save the timestamp of the start of the function as last checked activity on amara timestamp
                self.amara_activity_last_checked = start_timestamp
                self.next_amara_activity_check = start_timestamp + self.calculated_time_delta_for_activities
                self.save()

    # Check amara video-data
    @transaction.atomic
    def check_amara_video_data(self, force = False):
        start_timestamp = datetime.now(timezone.utc)
        # Only query amara if forced or flag is set
        if force or self.needs_complete_amara_update:
            url = "https://amara.org/api/videos/" + self.amara_key + "/languages/?format=json"
            if self.amara_key != "":
                import requests
                with advisory_lock(amara_api_lock) as acquired:
                    r = requests.get(url, headers = cred.AMARA_HEADER)
                    sleep(amara_api_call_sleep)
                counter = 0
                while True:
                    counter += 5
                    print(r.text)
                    if "Error 429 Too Many Requests" in r.text:
                        sleep(counter)
                        with advisory_lock(amara_api_lock) as acquired:
                            r = requests.get(url, headers = cred.AMARA_HEADER)
                            sleep(amara_api_call_sleep)
                    else:
                        activities = json.loads(r.text)
                        break
                    if counter == 120:
                        break
                for any_subtitle in activities["objects"]:
                    print("Talk_ID:", self.id, "Amara_key:", self.amara_key)
                    print("Language_code:", any_subtitle["language_code"])
                    amara_subt_lang = any_subtitle["language_code"]
                    print("is_primary_audio_language = is_original:", any_subtitle["is_primary_audio_language"])
                    amara_subt_is_original = any_subtitle["is_primary_audio_language"]
                    print("subtitles_complete:", any_subtitle["subtitles_complete"])
                    amara_subt_is_complete = any_subtitle["subtitles_complete"]
                    print("versions:", len(any_subtitle["versions"]))
                    amara_subt_revision = len(any_subtitle["versions"])
                    print("\n")
                    # Only proceed if the revision on amara is higher than zero
                    # Zero can exist if someone once clicked a language but didn't save anything
                    if amara_subt_revision > 0:
                        # Get the right subtitle dataset or create it, only if the version is not null
                        my_language = Language.objects.get(lang_amara_short = amara_subt_lang)
                        my_subtitle, created = Subtitle.objects.get_or_create(talk = self, language = my_language)
                        # Proceed if the version on amara has changed
                        if my_subtitle.revision != amara_subt_revision:
                            self.amara_update_interval = timedelta(minutes=5)
                            # If the subtitle was not complete and is not complete
                            if not my_subtitle.complete and not amara_subt_is_complete:
                                # Just update the data
                                my_subtitle.is_original_lang = amara_subt_is_original
                                my_subtitle.revision = amara_subt_revision
                                my_subtitle.save()
                                # If this is an subtitle which is the original language
                                # and is in a state which has already statistics, also recalculate them
                                if my_subtitle.is_original_lang and my_subtitle.state_id == (5 or 6 or 7):
                                    self.reset_related_statistics_data()
                                # Release a new draft if the subtitle is in state quality control
                                if my_subtitle.state_id == 7:
                                    my_subtitle.draft_needs_sync_to_sync_folder = True
                                my_subtitle.save()
                            # If the subtitle was not complete but is complete now
                            elif not my_subtitle.complete and amara_subt_is_complete:
                                my_subtitle.complete = amara_subt_is_complete
                                my_subtitle.is_orignal_lang = amara_subt_is_original
                                my_subtitle.revision = amara_subt_revision
                                # This sets the sync flags and the notifications-flag and also lets the statistics to be recalculated
                                my_subtitle.set_complete(was_already_complete = False)
                                # If the talk also is in the original language, recalculate statistics
                                if my_subtitle.is_original_lang:
                                    my_subtitle.talk.reset_related_statistics_data()
                                    # Remove the draft (translations don't have a draft)
                                    my_subtitle.draft_needs_removal_from_sync_folder = True
                                my_subtitle.save()
                            # If the subtitle was complete and is still complete
                            elif my_subtitle.complete and amara_subt_is_complete:
                                my_subtitle.complete = amara_subt_is_complete
                                my_subtitle.is_orignal_lang = amara_subt_is_original
                                my_subtitle.revision = amara_subt_revision
                                # This sets the sync flags and the notifications-flag and lets the statistics to be recalculated
                                my_subtitle.set_complete(was_already_complete = True)
                                # If the talk also is in the original language, recalculate statistics
                                if my_subtitle.is_original_lang:
                                    my_subtitle.talk.reset_related_statistics_data()
                                my_subtitle.save()
                            # If the subtitle was complete but isn't any more
                            elif my_subtitle.complete and not amara_subt_is_complete:
                                my_subtitle.complete = amara_subt_is_complete
                                my_subtitle.is_orignal_lang = amara_subt_is_original
                                my_subtitle.revision = amara_subt_revision
                                # Resets the states and also the statistics if it is the original language
                                my_subtitle.reset_from_complete()
                                my_subtitle.save()

                        # If the revision hasn't changed but the complete flag has changed, set the subtitle complete
                        elif amara_subt_is_complete and not my_subtitle.complete:
                            self.amara_update_interval = timedelta(minutes=5)
                            my_subtitle.set_complete()
                            if my_subtitle.is_original_lang:
                                my_subtitle.draft_needs_removal_from_sync_folder = True
                                my_subtitle.talk.reset_related_statistics_data()
                            my_subtitle.save()
                        # Set the right state if the default is still active on "1"
                        if my_subtitle.state_id == 1 and my_subtitle.is_original_lang:
                            my_subtitle.state_id = 2
                            my_subtitle.save()
                        elif my_subtitle.state_id == 1 and not my_subtitle.is_original_lang:
                            my_subtitle.state_id = 11
                            my_subtitle.save()
                # Save the timestamp when this function was last used and reset the flag
                self.amara_complete_update_last_checked = start_timestamp
                self.needs_complete_amara_update = False
                self.save()

    # Makes the language stored in the "Talk" the primary language on amara
    # Can use for initial configuration and for later changes, both works
    def make_talk_language_primary_on_amara(self, force_amara_update = True):
        # This only works if a amara key is already available
        if self.amara_key == "":
            return None
        # Amara API URL
        url = "https://amara.org/api/videos/" + self.amara_key + "/languages/" # + self.orig_language.lang_amara_short + "/"

        data_1 = {"is_primary_audio_language": True, "language_code": self.orig_language.lang_amara_short}
        data_2 = {"is_primary_audio_language": True}

        with advisory_lock(amara_api_lock) as acquired:
            #sleep(amara_api_call_sleep_fast_functions)
            r_1 = requests.post(url, headers = cred.SHORT_AMARA_HEADER, data = data_1)
            sleep(amara_api_call_sleep_fast_functions)
            url = url + self.orig_language.lang_amara_short + "/"
            r_2 = requests.put(url, headers = cred.SHORT_AMARA_HEADER, data = data_2)
            sleep(amara_api_call_sleep_fast_functions)

        if force_amara_update:
            self.needs_complete_amara_update = True
            self.save()

        return [r_1, r_2]

    # Upload the disclaimer text to amara into the first subtitle in the original language
    # This overwrites already existing subtitles!
    def upload_first_subtitle_to_amara_with_disclaimer(self, set_first_language = True, force_amara_update = True):
        # First, make sure the original language is acutally already set in amara!
        if set_first_language:
            self.make_talk_language_primary_on_amara(force_amara_update=False)

        subtitles_text = "Please use the Etherpad for the transcript.\nIf there is no transcript in the etherpad available yet, please tell us.\n\nTranskript here won't be further processed!\nIn the Etherpad you can find a auto generated Transcript as start.\n\n" + "https://c3subtitles.de/talk/" + str(self.id) + "\n"
        if self.link_to_writable_pad[0:1] == "#":
            subtitles_text += self.link_to_writable_pad[1:] + "\n"
        else:
            subtitles_text += self.link_to_writable_pad + "\n"
        parameters = {"subtitles": subtitles_text,
            "sub_format": "txt",
            "action": "save-draft"}
        url = "https://amara.org/api/videos/" + self.amara_key + "/languages/" + self.orig_language.lang_amara_short + "/subtitles/"
        print("URL: ", url)
        print("Parameters: ", parameters)
        print("Subtitles_Text: ", subtitles_text)
        with advisory_lock(amara_api_lock) as acquired:
            r = requests.post(url, headers = cred.AMARA_HEADER, data = json.dumps(parameters))
            sleep(amara_api_call_sleep)

        if force_amara_update:
            self.needs_complete_amara_update = True
            self.save()

        return r

    # Get the video links which are on amara from there and store them in the c3subtitles database
    # This is expecially used for an initial import
    def get_video_links_from_amara(self, do_save = True):
        return read_links_from_amara(talk=self, do_save=do_save)

    # Update the video links in amara according to the ones in the c3subtitles database
    # This is also used to create an initial amara_key
    def update_video_links_in_amara(self):
        return update_amara_urls(talk=self)

    # Create amara_key with the primary video link
    def create_amara_key(self):
        return create_and_store_amara_key(talk=self)

    # This function takes the talk.link_to_video_file downloads the file,
    # pushes it to trint via api and waits for the srt transcript
    # After receiving the srt file it also creates a transcript without timing information
    # It sends an email with both files to the logs list
    # If there is no video link it does nothing
    # If there is already a trint_transcript_id it will not upload the file again
    # but it will download it again and send it via email
    def get_trint_transcript_and_send_via_email(self, make_pad_link_available=True, release_draft=True, do_send_email=True, polling_in_background=True):
        return get_trint_transcript_via_api(self, make_pad_link_available=make_pad_link_available, release_draft=release_draft, do_send_email=do_send_email, polling_in_background=polling_in_background)

    def do_notify_transcript_available(self):
        from . import notifications_bot_helper
        notifications_bot_helper.notify_transcript_available(self)
        self.refresh_from_db()
        self.notify_transcript_available = False
        self.save()

    def __str__(self):
        return self.title


# States for every subtitle like "complete" or "needs sync"
class States(BasisModell):
    state_de = models.CharField(max_length = 100)
    state_en = models.CharField(max_length = 100)
    def __str__(self):
        return self.state_en


# Infos to a subtitle in one language
class Subtitle(BasisModell):
    talk = models.ForeignKey(Talk, on_delete=models.PROTECT)
    language = models.ForeignKey(Language, on_delete=models.PROTECT)#, to_field = "lang_amara_short")
    is_original_lang = models.BooleanField(default = False, verbose_name='original language') # Read from Amara, not from the Fahrplan!
    revision = models.PositiveSmallIntegerField(default = 0)
    complete = models.BooleanField(default = False)
    state = models.ForeignKey(States, default = 1, blank = True, on_delete=models.SET_DEFAULT)
    time_processed_transcribing = models.TimeField(default=time(0), blank=True, verbose_name="")
    time_processed_syncing = models.TimeField(default=time(0), blank=True, verbose_name="")
    time_quality_check_done = models.TimeField(default=time(0), blank=True, verbose_name="")
    time_processed_translating = models.TimeField(default=time(0), blank=True, verbose_name="")
    blocked = models.BooleanField(default = False)
    last_changed_on_amara = models.DateTimeField(default=make_aware(datetime.min), blank=True)
    #yt_caption_id = models.CharField(max_length = 50, default = "", blank = True)
    unlisted = models.BooleanField(default = False) # If syncs to the cdn, and media or YT should be blocked
    needs_sync_to_sync_folder = models.BooleanField(default = False)
    needs_removal_from_sync_folder = models.BooleanField(default = False)
    autotiming_step = models.PositiveSmallIntegerField(default=0)
    draft_needs_sync_to_sync_folder = models.BooleanField(default = False)
    draft_needs_removal_from_sync_folder = models.BooleanField(default = False)
    notify_subtitle_needs_timing = models.BooleanField(default = False)
    notify_subtitle_ready_for_quality_control = models.BooleanField(default = False)
    notify_subtitle_released = models.BooleanField(default = False)
    has_draft_subtitle_file = models.BooleanField(default = False) # e.g. from trint or YT

    def _still_in_progress(self, timestamp, state, original_language=True):
        if original_language != self.is_original_lang:
            return False

        return ((timestamp < self.talk.video_duration) or
                (self.state_id == state and timestamp <= self.talk.video_duration))

    @property
    def transcription_in_progress(self):
        return self._still_in_progress(self.time_processed_transcribing, state=2)

    @property
    def syncing_in_progress(self):
        return self._still_in_progress(self.time_processed_syncing, state=5)

    @property
    def quality_check_in_progress(self):
        return self._still_in_progress(self.time_quality_check_done, state=7)

    @property
    def translation_in_progress(self):
        return self._still_in_progress(self.time_processed_translating, state=11, original_language=False)

    @property
    def language_short(self):
        # Workaround because of Klingon / Orignal
        lang = self.language.lang_short_srt
        return self.language.lang_short_srt

    # Get the filename for the fileservers
    def get_filename_srt(self, draft = False):
        if self.talk.filename != "":
            if draft:
                filename = "DRAFT_" + self.talk.filename + "." + self.language.lang_short_srt + "_DRAFT.srt"
            else:
                filename = self.talk.filename + "." + self.language.lang_short_srt + ".srt"
            return filename
        else:
            return None

    # Get the filename for the fileservers
    def get_filename(self, draft = False, format = "srt"):
        if self.talk.filename != "":
            if draft:
                filename = "DRAFT_" + self.talk.filename + "." + self.language.lang_short_srt + "_DRAFT." + format
            else:
                filename = self.talk.filename + "." + self.language.lang_short_srt + "." + format
            return filename
        else:
            return None

    # Return the transcript file with amara fails fixed
    def as_transcript(self, save = False, without_line_breaks = False):
        import re
        import requests
        # Create the url for the srt File
        # Only the srt-Version of all possible fileformats includes the "*" and "&"
        url = "https://amara.org/api/videos/" + self.talk.amara_key +"/languages/" + self.language.lang_amara_short + "/subtitles/?format=srt"
        # If this fails for any reason return None
        try:
        # No header necessary, this works without identification
            with advisory_lock(amara_api_lock) as acquired:
                r = requests.get(url)
                sleep(amara_api_call_sleep)
        except:
            return None
        srt_file =  r.text
        # Split the file at every double linebreak
        srt_file = srt_file.split("\r\n\r\n")
        transcript = ""
        for any_block in srt_file:
            # Split every textblock in its lines
            any_block = any_block.split("\r\n")
            line_counter = 2
            while line_counter < len(any_block):
                # Ignore empty subtitle lines
                if any_block[line_counter] != "":
                    transcript += any_block[line_counter] + "\n"
                line_counter += 1
            # Double line break after a complete block
            transcript += "\n"
        # Fix some amara fails
        transcript = re.sub("<i>", "*", transcript)
        transcript = re.sub("</i>", "*", transcript)
        transcript = re.sub("&amp;", "&", transcript)
        if save:
            filename = self.talk.slug+"." + self.language.lang_amara_short + ".transcript"
            folder = "./downloads/subtitle_transcript_files/"
            # Save File in ./downloads
            file = open(folder+filename,mode = "w",encoding = "utf-8")
            file.write(transcript)
            file.close()
        if without_line_breaks:
            transcript = re.sub("\n", " ", transcript)
            transcript = re.sub("  ", " ", transcript)
            transcript = re.sub("  ", " ", transcript)
        return transcript

    # Return the sbv_file with fixes (no fixes necessary, but "*" get lost)
    def as_sbv(self, save = False):
        import requests
        # Create the url for the sbv File
        url = "https://amara.org/api/videos/" + self.talk.amara_key +"/languages/" + self.language.lang_amara_short + "/subtitles/?format=sbv"
        # If this fails for any reason return None
        try:
        # No header necessary, this works without identification
            with advisory_lock(amara_api_lock) as acquired:
                r = requests.get(url)
                sleep(amara_api_call_sleep)
        except:
            return None
        sbv_file =  r.text
        if save:
            filename = self.talk.slug+"." + self.language.lang_amara_short + ".sbv"
            folder = "./downloads/subtitle_sbv_files/"
            # Save File in ./downloads
            file = open(folder+filename,mode = "w",encoding = "utf-8")
            file.write(sbv_file)
            file.close()
        return sbv_file

    # Return the srt_file with fixes
    def as_srt(self, save = False, with_draft_disclaimer = False):
        import re
        import requests
        # Create the url for the srt File
        # Only the srt-Version of all possible fileformats includes the "*" and "&"
        url = "https://amara.org/api/videos/" + self.talk.amara_key +"/languages/" + self.language.lang_amara_short + "/subtitles/?format=srt"
        # If this fails for any reason return None
        try:
        # No header necessary, this works without identification
            with advisory_lock(amara_api_lock) as acquired:
                r = requests.get(url)
                sleep(amara_api_call_sleep)
        except:
            return None
        srt_file =  r.text
        # Fix some amara fails
        srt_file = re.sub("<i>", "*", srt_file)
        srt_file = re.sub("</i>", "*", srt_file)
        srt_file = re.sub("&amp;", "&", srt_file)
        if with_draft_disclaimer:
            disclaimer = "0\n00:00:00,000 --> 00:00:30,000\n"
            if self.talk.orig_language.lang_short_srt == "de":
                disclaimer += "Dieser Untertitel ist noch nicht fertig.\nWenn du kannst, bitte unterstütze uns hier\n"
                disclaimer += "und schau den Talk in Amara an für die\nletzten Korrekturen:\n" + "https://c3subtitles.de/talk/" + str(self.talk.id) + " Danke!"
            else:
                disclaimer += "This subtitle is not finished yet. If you\nare able to, please support us and watch\n"
                disclaimer += "the talk in amara for the last changes:\n" + "https://c3subtitles.de/talk/" + str(self.talk.id) + " Thanks!"
            disclaimer += "\n\n"
            srt_file = disclaimer + srt_file
        if save:
            filename = self.talk.slug+"." + self.language.lang_amara_short + ".srt"
            folder = "./downloads/subtitle_srt_files/"
            # Save File in ./downloads
            file = open(folder+filename, mode = "w", encoding = "utf-8")
            file.write(srt_file)
            file.close()
        return srt_file

    # Saves Subtitles Files to the sync folder
    def sync_subtitle_to_sync_folder(self, force = False):
        # Sync the subtitle if it is not unlisted and the sync flag is true of when it is forced
        if (not self.unlisted and self.needs_sync_to_sync_folder) or force:
            import shutil
            import os
            # Download the subtitle as srt file
            self.as_srt(save = True)
            # Copy the subtitle to the right folder
            file_from = os.path.join(os.path.dirname(os.path.dirname(__file__)),"downloads/subtitle_srt_files/") + self.talk.slug + "." + self.language.lang_amara_short + ".srt"
            file_to = os.path.join(os.path.dirname(os.path.dirname(__file__)),"subtitles_sync_folder/") + self.talk.event.subfolder_in_sync_folder + "/" + self.get_filename_srt()
            try:
                shutil.copy2(file_from, file_to)
            except:
                print("Exception")
                return False
            # Remove the sync flag and save
            self.needs_sync_to_sync_folder = False
            self.save()
            return True
        else:
            return False

    # Saves Subtitles Files to the sync folder
    def sync_subtitle_draft_to_sync_folder(self, force = False):
        # Sync the subtitle if it is not unlisted and the sync flag is true of when it is forced
        if (not self.unlisted and self.draft_needs_sync_to_sync_folder) or force:
            import shutil
            import os
            # Download the subtitle as srt file
            self.as_srt(save = True, with_draft_disclaimer = True)
            # Copy the subtitle to the right folder
            file_from = os.path.join(os.path.dirname(os.path.dirname(__file__)),"downloads/subtitle_srt_files/") + self.talk.slug + "." + self.language.lang_amara_short + ".srt"
            file_to = os.path.join(os.path.dirname(os.path.dirname(__file__)),"subtitles_sync_folder/") + self.talk.event.subfolder_in_sync_folder + "/" + self.get_filename_srt(draft=True)
            try:
                shutil.copy2(file_from, file_to)
            except:
                print("Exception")
                return False
            # Remove the sync flag and save
            self.draft_needs_sync_to_sync_folder = False
            self.save()
            return True
        else:
            return False

    # Removes Subtitles Files from the sync folder
    def remove_subtitle_from_sync_folder(self, force = False):
        if self.needs_removal_from_sync_folder or force:
            import os
            file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)),"subtitles_sync_folder/") + self.talk.event.subfolder_in_sync_folder + "/" + self.get_filename_srt()
            try:
                os.remove(file_name)
            except:
                pass
            self.needs_removal_from_sync_folder = False
            self.save()
        if self.draft_needs_removal_from_sync_folder or force:
            import os
            file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)),"subtitles_sync_folder/") + self.talk.event.subfolder_in_sync_folder + "/" + self.get_filename_srt(draft=True)
            try:
                os.remove(file_name)
            except:
                pass
            self.draft_needs_removal_from_sync_folder = False
            self.save()

    # Puts a non amara file as subtitle into the releasing folder
    # Input is possible as string or as path to a file
    def put_subtitle_draft_into_sync_folder(self, draft = True, text = "", file_with_full_path = "", format = "srt", with_draft_disclaimer = True):
        full_releasing_path = self.get_full_file_path(draft=draft, format=format)
        if file_with_full_path != "":
            import shutil
            shutil.copy2(file_with_full_path, full_releasing_path)
        if text != "":
            file = open(full_releasing_path, mode = "w", encoding = "utf-8")
            for line in text:
                file.write(line)
            file.close()
        if with_draft_disclaimer:
            # Create the Disclaimer-text:
            text = "0\n00:00:00,000 --> 00:00:30,000\n"
            if self.language.lang_amara_short == "de":
                text += "Lieber Zuschauer, dieser Untertitel wurde\n"
                text += "automatisch generiert von " + str(self.talk.transcript_by) + "\n"
                text += "und dementsprechend (sehr) fehlerhaft.\n"
                text += "Wenn du kannst, hilf uns bitte gute\n"
                text += "Untertitel zu erstellen:\n"
                text += "https://c3subtitles.de/talk/" + str(self.talk.id) + " Danke!\n\n"
            else:
                text += "Dear viewer, these subtitles were generated\n"
                text += "by a machine via the service " + str(self.talk.transcript_by) + "\n"
                text += "and therefore are (very) buggy.\n"
                text += "If you are capable, please help us to\n"
                text += "create good quality subtitles:\n"
                text += "https://c3subtitles.de/talk/" + str(self.talk.id) + " Thanks!\n\n"
            # Open the file again and add the disclaimer if the first line is not already "0"
            file = open(full_releasing_path,mode = "r",encoding = "utf-8")
            file_content = file.readline()
            file.close()
            if file_content != "0\n":
                file = open(full_releasing_path,mode = "r",encoding = "utf-8")
                file_content = file.read()
                file.close()
                file_content = text + file_content
                file = open(full_releasing_path,mode = "w",encoding = "utf-8")
                for any_line in file_content:
                    file.write(any_line)
                file.close()

    def get_full_file_path(self, draft=False, download_folder=False, format="srt"):
        import os
        if download_folder:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"subtitles_sync_folder/downloads/subtitles_external_drafts") + "/"
        else:
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"subtitles_sync_folder/") + self.talk.event.subfolder_in_sync_folder + "/"
        filename = self.get_filename(draft = draft, format = format)
        return path + filename

    # Set all flags for a sync to cdn, media frontend, YT ...
    def set_all_sync_flags(self, save = False, draft = False):
        #self.needs_sync_to_ftp = True
        #self.needs_sync_to_media = True
        #self.needs_sync_to_YT = True
        if draft:
            self.draft_needs_sync_to_sync_folder = True
        else:
            self.needs_sync_to_sync_folder = True
        if save:
            self.save()

    # Set all flags for a removal from the cdn, media frontend, YT...
    def set_all_removal_flags(self, save = False):
        #self.needs_removal_from_ftp = True
        #self.needs_removal_from_media = True
        #self.needs_removal_from_YT = True
        self.draft_needs_removal_from_sync_folder = True
        self.needs_removal_from_sync_folder = True
        if save:
            self.save()

    # Send an email with the subtitle which needs timing and post a message to the orga chat(s)
    def do_notify_subtitle_needs_timing(self):
        # Send Mail
        from . import notifications_bot_helper
        notifications_bot_helper.create_and_send_email_for_subtitle_needs_autotiming(self)
        
        # Send other Notifications
        notifications_bot_helper.notify_transcript_needs_timing(self)
        
        # Reset Flag
        self.refresh_from_db()
        self.notify_subtitle_needs_timing = False
        self.save()

    # Send a notification that the subtitle is ready for quality control
    def do_notify_subtitle_ready_for_quality_control(self):
        from . import notifications_bot_helper
        notifications_bot_helper.notify_subtitle_ready_for_quality_control(self)
        self.refresh_from_db()
        self.notify_subtitle_ready_for_quality_control = False
        self.save()

    # Send a notification for a released subtitle
    def do_notify_subtitle_released(self):
        # Check if the subtitle is really online:
        if self.srt_is_synced_to_mirror:
            from . import notifications_bot_helper
            notifications_bot_helper.notify_subtitle_released(self)
            self.refresh_from_db()
            self.notify_subtitle_released = False
            self.save()

    # Set the subtitle complete
    @transaction.atomic
    def set_complete(self, was_already_complete = False):
        if self.is_original_lang:
            self.time_processed_transcribing = self.talk.video_duration
            self.time_processed_syncing = self.talk.video_duration
            self.time_quality_check_done = self.talk.video_duration
            self.draft_needs_removal_from_sync_folder = True # Delete the draft
            self.has_draft_subtitle_file = False
            self.state_id = 8
            # Let the related statistics data be recalculated
            self.talk.reset_related_statistics_data()
        else:
            self.time_processed_translating = self.talk.video_duration
            self.state_id = 12
        # Only notify if the file was not already complete
        if not was_already_complete:
            self.notify_subtitle_released = True
            self.complete = True
        self.blocked = False
        self.set_all_sync_flags()
        self.notify_subtitle_needs_timing = False
        self.save()

    # Reset subtitle if it was complete but it is not any more
    @transaction.atomic
    def reset_from_complete(self):
        self.time_processed_transcribing = "00:00:00"
        self.time_processed_syncing = "00:00:00"
        self.time_quality_check_done = "00:00:00"
        self.time_processed_translating = "00:00:00"
        self.has_draft_subtitle_file = False
        if self.is_original_lang:
            self.state_id = 2
            # Hard reset for the related statistics data
            self.talk.reset_related_statistics_data(True)
            self.draft_needs_removal_from_sync_folder = True
        else:
            self.state_id = 11
        self.set_all_removal_flags()
        self.notify_subtitle_needs_timing = False
        self.blocked = False
        self.save()

    # Set to autotiming in progress
    @transaction.atomic
    def set_to_autotiming_in_progress(self):
        # Stop if the subtitle is not the original language
        if not self.is_original_lang:
            return None
        needs_save = False
        if self.time_processed_transcribing != self.talk.video_duration:
            self.time_processed_transcribing = self.talk.video_duration
            needs_save = True
        if self.blocked == False:
            self.blocked = True
            needs_save = True
        if self.notify_subtitle_needs_timing == False:
            self.notify_subtitle_needs_timing = True
            needs_save = True
        if self.state_id != 4:
            self.state_id = 4
            needs_save = True
        if needs_save:
            self.save()
        return needs_save

    def get_absolute_url(self):
        return reverse('subtitle', args=[str(self.id)])

    # Check if the subtitle is really available on the mirror
    @property
    def srt_is_synced_to_mirror(self):
        link = "https://mirror.selfnet.de/c3subtitles/" + self.talk.event.subfolder_in_sync_folder + "/" + self.get_filename_srt()
        try:
            request = requests.head(link)
        except:
            return False
        if request.status_code == 200:
            return True
        return False


# Links from the Fahrplan
class Links(BasisModell):
    talk = models.ForeignKey(Talk, blank = True, on_delete=models.PROTECT)
    url = models.URLField(blank = True, max_length = 300)
    title = models.CharField(max_length = 200, default = "Link title", blank = True)


# Statistics about Speakers and their words per minute and strokes per minute
# These datasets have to be collected by "hand", they can not be auto created
# speaker, talk, start and end need to be entered manually
class Statistics_Raw_Data(BasisModell):
    speaker = models.ForeignKey(Speaker, on_delete=models.PROTECT)
    talk = models.ForeignKey(Talk, on_delete=models.PROTECT)
    start = models.TimeField(blank = True, null = True)
    end = models.TimeField(blank = True, null = True)
    time_delta = models.FloatField(blank = True, null = True) # only seconds!
    words = models.IntegerField(blank = True, null = True)
    strokes = models.IntegerField(blank = True, null = True)
    recalculate_statistics = models.BooleanField(default = False)

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        # Only calculate if it is forced or if the recalculate flag
        # is set to true
        if force or self.recalculate_statistics:
            values = calculate_subtitle(self.talk, self.start, self.end)
            if values is not None:
                self.time_delta = values["time_delta"]
                self.words = values["words"]
                self.strokes = values["strokes"]
                self.recalculate_statistics = False
                self.save()
                # Set recalculate flags in the connected Statistics_Event module
                Talk.objects.filter(id = self.talk_id).update(recalculate_speakers_statistics = True)
                # Set recalculate flag in the connected Talk_Persons Statistics
                Talk_Persons.objects.filter(talk = self.talk, speaker = self.speaker).update(recalculate_statistics = True)
                # Set recalculate flag in the connected Statistics_Speaker module and also create the database entry
                # Get or create the related Statistics_Speaker database entry.
                # The necessary language is not the language of the talk but the language of the related is_orignal subtitle!
                this_speaker, created = Statistics_Speaker.objects.get_or_create(speaker = self.speaker, language = self.talk.language_of_original_subtitle)
                this_speaker.recalculate_statistics = True
                this_speaker.save()

            # Save the word frequencies into a json file
            if values["word_frequencies"] is not None and len(values["word_frequencies"]) > 0:
                save_word_dict_as_json(values["word_frequencies"],"statistics_raw_data", self.id)

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("statistics_raw_data", self.id)


# Speakers can have different Statistic values for different languages they spoke during talks
# This is calculated from the Statistics_Raw_Data which only counts the actual time the speaker speaks
# The subtitle must be finished or in review
class Statistics_Speaker(BasisModell):
    speaker = models.ForeignKey(Speaker, on_delete=models.PROTECT)
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    words = models.IntegerField(blank = True, null = True)      # All words from this speaker in this language summed up
    strokes = models.IntegerField(blank = True, null = True)    # All strokes from this speaker in this language summed up
    time_delta = models.FloatField(blank = True, null = True)   # Summed up time deltas from this speaker in this language
    average_wpm = models.FloatField(blank = True, null = True)  # Calculated from words and time delta
    average_spm = models.FloatField(blank = True, null = True)  # Caluclated from strokes and time_delta
    recalculate_statistics = models.BooleanField(default = False)
    n_most_frequent_words = models.TextField(default = "{}")    # n most common words as json string

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        # Recalculate absolutely everything
        if force or self.recalculate_statistics:
            # Empty dictionary for the word_frequencies
            word_freq = {}
            # All timeslots form Statistics_Raw_Data which has the same speaker and via the talk also the same language
            # All Subtitles which are the orignal language and the right language
            my_subtitles = Subtitle.objects.filter(is_original_lang = True, language = self.language)
            # Use temporary values
            words = strokes = time_delta = 0
            # Iterate over all these subtitles and get the right talk_id, then check if it has the right speaker
            for any in my_subtitles:
                talk_persons = Talk_Persons.objects.filter(speaker = self.speaker, talk = any.talk)
                # Just to be careful, first check if anything needs a recalculation first
                for any2 in talk_persons:
                    any2.recalculate()
                    # While looping over all connected talk_persons also add the word_frequencies up
                    word_freq = merge_word_frequencies_dicts(word_freq, any2.word_frequencies)
                # Only sum up if there is something to sum up
                if talk_persons.count() > 0:
                    # Do not add up if None
                    temp = talk_persons.aggregate(Sum("words"))["words__sum"]
                    if temp is not None:
                        words += temp
                    temp = talk_persons.aggregate(Sum("strokes"))["strokes__sum"]
                    if temp is not None:
                        strokes += temp
                    temp = talk_persons.aggregate(Sum("time_delta"))["time_delta__sum"]
                    if temp is not None:
                        time_delta += temp
            # If really everything was none:
            if (words or strokes or time_delta) is None:
                self.words = self.strokes = self.time_delta = self.average_wpm = self.average_spm = None
            else:
                self.words = words
                self.strokes = strokes
                self.time_delta = time_delta
                self.average_wpm = calculate_per_minute(self.words, self.time_delta)
                self.average_spm = calculate_per_minute(self.strokes, self.time_delta)

            # Save the word frequencies into a json file
            if word_freq is not None and len(word_freq) > 0:
                save_word_dict_as_json(word_freq,"statistics_speaker", self.id)
                self.n_most_frequent_words = json.dumps(n_most_common_words(word_freq), ensure_ascii = False)
            else:
                self.n_most_frequent_words = "{}"
            self.recalculate_statistics = False
            self.save()

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("statistics_speaker", self.id)

    # Return the n most common words as dict
    @property
    def n_common_words(self):
        return json.loads(self.n_most_frequent_words)


# Every Event can have different Statistic values for different languages
# The statistics applies to whole talk-time, not only the speakers time, it
# includes breaks, and Q&A and other stuff
class Statistics_Event(BasisModell):
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    words = models.IntegerField(blank = True, null = True)  # Summed up from finished / in review whole talks, not only speakers time
    strokes = models.IntegerField(blank = True, null = True)    # Calculated from finished / in review whole talks, not only speakers time
    time_delta = models.FloatField(blank = True, null = True)   # Seconds of all talks from this event which are in review or finished
    average_wpm = models.FloatField(blank = True, null = True)  # Calculated from words and time_delta
    average_spm = models.FloatField(blank = True, null = True)  # Calculated from strokes and time_delta
    recalculate_statistics = models.BooleanField(default = False)
    n_most_frequent_words = models.TextField(default = "{}")    # n most common words as json string

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        if force or self.recalculate_statistics:
            # Find all Subtitles connected with this event and this language
            my_subtitles = Subtitle.objects.filter(talk__event = self.event, language = self.language, is_original_lang = True)
            # If nothing is found
            if my_subtitles.count() == 0:
                self.words = None
                self.strokes = None
                self.time_delta = None
                self.average_wpm = None
                self.average_spm = None
            else:
                self.words = my_subtitles.aggregate(Sum("talk__words"))["talk__words__sum"]
                self.strokes = my_subtitles.aggregate(Sum("talk__strokes"))["talk__strokes__sum"]
                self.time_delta = my_subtitles.aggregate(Sum("talk__time_delta"))["talk__time_delta__sum"]
                # If there is not really a finished subtitle in the language
                if (self.words or self.strokes or self.time_delta) is None:
                    self.words = self.strokes = self.time_delta = self.average_wpm = self.average_spm = None
                else:
                    self.average_wpm = calculate_per_minute(self.words, self.time_delta)
                    self.average_spm = calculate_per_minute(self.strokes, self.time_delta)

            # Dictionary for the word freqiencies
            word_freq = {}
            # Merge all sub word_frequencies
            for any in my_subtitles:
                word_freq = merge_word_frequencies_dicts(any.talk.word_frequencies, word_freq)
            # Save the word frequencies into a json file
            if word_freq is not None and len(word_freq) > 0:
                save_word_dict_as_json(word_freq,"statistics_event", self.id)
                self.n_most_frequent_words = json.dumps(n_most_common_words(word_freq), ensure_ascii = False)
            else:
                self.n_most_frequent_words = "{}"
            self.recalculate_statistics = False
            self.save()

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("statistics_event", self.id)

    # Return the n most common words as dict
    @property
    def n_common_words(self):
        return json.loads(self.n_most_frequent_words)

    @property
    def has_statistics(self):
        if self.average_wpm is not None and self.average_spm is not None:
            return True
        else:
            return False


# m:n Connection between Talks and Speakers and their Statistics data
class Talk_Persons(BasisModell):
    talk = models.ForeignKey(Talk, on_delete=models.PROTECT)
    speaker = models.ForeignKey(Speaker, on_delete=models.PROTECT)
    words = models.IntegerField(blank = True, null = True)      # All words from this speaker in this talk summed up
    strokes = models.IntegerField(blank = True, null = True)    # All strokes from this speaker in this talk summed up
    time_delta = models.FloatField(blank = True, null = True)   # Summed up time deltas from this speaker in this talk
    average_wpm = models.FloatField(blank = True, null = True)  # Calculated from words and time delta
    average_spm = models.FloatField(blank = True, null = True)  # Caluclated from strokes and time_delta
    recalculate_statistics = models.BooleanField(default = False)
    n_most_frequent_words = models.TextField(default = "{}")    # n most common words as json string

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        # Recalculate absolutely everything
        if force or self.recalculate_statistics:
            # Get statistics_raw for this speaker and this talk and sum it up
            raw_data = Statistics_Raw_Data.objects.filter(talk = self.talk, speaker = self.speaker)
            # If for some reason something needs a recalculation
            for any in raw_data:
                any.recalculate()
            if raw_data.count() == 0:
                self.words = self.strokes = self.time_delta = self.average_wpm = self.average_spm = None
            else:
                self.words = raw_data.aggregate(Sum("words"))["words__sum"]
                self.strokes = raw_data.aggregate(Sum("strokes"))["strokes__sum"]
                self.time_delta = raw_data.aggregate(Sum("time_delta"))["time_delta__sum"]
                if (self.words or self.strokes or self.time_delta) is None:
                    self.words = self.strokes = self.time_delta = self.average_wpm = self.average_spm = None
                else:
                    self.average_wpm = calculate_per_minute(self.words, self.time_delta)
                    self.average_spm = calculate_per_minute(self.strokes, self.time_delta)

            # Dictionary for the word freqiencies
            word_freq = {}
            # Merge all sub word_frequencies
            for any in raw_data:
                word_freq = merge_word_frequencies_dicts(any.word_frequencies, word_freq)
            # Save the word frequencies into a json file
            if word_freq is not None and len(word_freq) > 0:
                save_word_dict_as_json(word_freq,"talk_persons", self.id)
                self.n_most_frequent_words = json.dumps(n_most_common_words(word_freq), ensure_ascii = False)
            else:
                self.n_most_frequent_words = "{}"
            self.recalculate_statistics = False
            self.save()

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("talk_persons", self.id)

    # Return the n most common words as dict
    @property
    def n_common_words(self):
        return json.loads(self.n_most_frequent_words)

    @property
    def has_statistics(self):
        if self.average_wpm is not None and self.average_spm is not None:
            return True
        else:
            return False
