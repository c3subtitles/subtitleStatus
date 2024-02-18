from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from www import transforms
import datetime
from django.utils import timezone
from .models import Event, Talk, Subtitle, Language, Speaker, Talk_Persons, Statistics_Event, Statistics_Speaker, Event_Days, Statistics_Raw_Data
from .forms import SubtitleForm, SimplePasteForm

#from copy import deepcopy
#import django_filters

# Create your views here.

# Start of the Website with all the events
def start(request):
    try:
        my_events = list(Event.objects.all().order_by("-start"))

        # Function for the progress bars
        for every_event in my_events:
            # Special case for the event "Random Talks"
            if every_event.id == 20:
                my_talks = Talk.objects.filter(event__unlisted=True, unlisted = False)
            else:
                my_talks = Talk.objects.filter(event = every_event, unlisted = False)
            every_event.__dict__.update(progress_bar_for_talks(my_talks))
            # Every Statistics dataset except for those without data
            try:
                every_event.statistics = Statistics_Event.objects.filter(event = every_event) \
                    .exclude(average_wpm = None, average_spm = None) \
                    .order_by("language__language_en")
            except:
                every_event.statistics = None

    except ObjectDoesNotExist:
        raise Http404

    return render(request, "main.html", {"events" : my_events, "request": request} )

# Overview over the Talks of one event
def event(request, acronym, day=0, language=None):
    my_event = get_object_or_404(Event, acronym=acronym)
    # Special case for the event "Random Talks"
    if my_event.id == 20:
        my_talks = Talk.objects.filter(unlisted=False, event__unlisted=True).order_by(
            "day",
            "date",
            "start",
            "room__room")
        original_languages = [lang['orig_language']
                          for lang in my_talks.values('orig_language')]
    else:
        my_talks = my_event.talk_set.filter(unlisted=False).order_by(
            "day",
            "date",
            "start",
            "room__room")
        original_languages = [lang['orig_language']
                              for lang in my_talks.values('orig_language')]
    # Special case for 36c3, only show the talks with all data complete
    if my_event.id in [11, 12, 13]:
        my_talks = my_talks.all().exclude(
            video_duration="00:00:00"
        ).exclude(amara_key="").exclude(filename="")
    my_langs = Language.objects.filter(pk__in=original_languages)
    if day > 0:
        my_talks = my_talks.filter(day__index=day)
    if language:
        my_talks = my_talks.filter(orig_language__lang_amara_short=language)
    my_event.__dict__.update(progress_bar_for_talks(my_talks))

    for talk in my_talks:
        talk.subtitles = talk.subtitle_set.order_by('-is_original_lang')
        # Create chunk for the 3 columns display of talks on event page
    talks_per_line = 3
    talks_chunk = [my_talks[x:x+talks_per_line]
                   for x in range(0, len(my_talks), talks_per_line)]

    return render(request, "event.html",
                  {"my_talks": my_talks,
                   "my_event": my_event,
                   "my_days": my_event.event_days_set.all().order_by("date"),
                   "my_langs": my_langs,
                   "page_sub_titles": my_event.page_sub_titles,
                   "talks_chunk": talks_chunk,
                   "request": request,
                   "datetime_min": datetime.datetime.min,
                  })

# Form to save the progress of a subtitle
def get_subtitle_form(request, talk, sub):
    """

 * Wenn time_processed_transcribing < Talk.video_duration:
     o state_en nur id 1,2,3 oder 9 anzeigen, dahinter das Zeitfeld für
       time_processed_transcribing mit dem Wert aus der Datenbank und
       einem Button für "ok" und einem für "Transcribing done".
         + Wenn der User auf den "Transcribing done" Button drückt dann
           sollte die Talk.video_duration in das Feld für
           time_processed_transcribing geschrieben werden und der State
           sollte auf id 4 springen und ein Flag setzen (muss ich noch
           in das model rein machen) oder als workaround eine mal schicken.
 * Wenn time_processed_transcribing und time_processed_syncing =
   Talk.video_duration:
     o state_en nur id 6 und 7 anzeigen, dahinter den Zeitstempel für
       time_quality_check_done mit wert aus DB und buttons wie oben nur
       halt mit "Quality check done"
         + Wenn der User auf den "Translation finished" Button drückt
           dann sollte die Talk.video_duration in das Feld für
           time_quality_check_done geschrieben werden und der State
           sollte auf id 12 und complete = True markieren.
 * Für den Teil mit time_processed_syncing kann man das auch
   implementieren, ich hoffe es vorerst nicht zu brauchen, das wäre
   dann halt mit state id 5 und 6 und soll aber falls es als syncing
   fertig markiert wird auf state id 7 springen, die 6 (timing fertig)
   ist nur für den user da.

*Übersetzung:* (kein is original flag)
Ich grübel da noch ob das quality-check teil dazu sollte oder ob man beim Übersetzten auch einfach eine Person drann lässt?!
Für den Fall ohne Quality check wäre es:

 * einmal das ganze mit state id 11 und 12 in der Anzeige vom dropdown
   menü und dem timestamp dazu aus der Datenbank von
   time_processed_translating + passende buttons.

    """
    form = SubtitleForm(request.POST or None, instance=sub)

    if sub.blocked: #time_processed_transcribing == talk.video_duration != sub.time_processed_syncing:
        return "Automatic syncing, please wait and come back later!"
    if sub.complete:
        return "Finished :)"

    if sub.transcription_in_progress:
        # remove the unnecessary fields
        #form.fields.pop("time_processed_transcribing")
        form.fields.pop("time_processed_syncing")
        form.fields.pop("time_quality_check_done")
        form.fields.pop("time_processed_translating")
     # add finish transcribing button
        form.quick_btn = 'Finish Transcribing'
        return form
    elif sub.quality_check_in_progress:
        # remove the unnecessary fields
        form.fields.pop("time_processed_transcribing")
        form.fields.pop("time_processed_syncing")
        #form.fields.pop("time_quality_check_done")
        form.fields.pop("time_processed_translating")
     # add finish transcribing button
        form.quick_btn = 'Finish quality check'
        return form
    elif sub.translation_in_progress:
        # remove the unnecessary fields
        form.fields.pop("time_processed_transcribing")
        form.fields.pop("time_processed_syncing")
        form.fields.pop("time_quality_check_done")
        #form.fields.pop("time_processed_translating")
     # add finish transcribing button
        form.quick_btn = 'Finish Translating'
        return form

    return


def talk(request, id):
    my_talk = get_object_or_404(Talk, pk=id, unlisted=False)
    my_subtitles = my_talk.subtitle_set.all().order_by("-is_original_lang","language__lang_amara_short")

    speakers_in_talk_statistics = Talk_Persons.objects.filter(talk = my_talk)

    # Make sure only subtitles in the right state have a download link with
    # the right filename for the download
    for any in my_subtitles:
        # Check if the subtitle is in quality control or has an external subtitle
        # draft and is in the right state
        if (any.state.id > 0 and any.state.id <= 5 and any.has_draft_subtitle_file and any.is_original_lang) or (any.state.id ==7 and not any.unlisted):
            any.external_draft_subtitles_online = True
        else:
            any.external_draft_subtitles_online = False
        any.form = get_subtitle_form(request, my_talk, any)
        # Get or create the filenames also for draft subtitles
        if any.state_id == 7 or any.external_draft_subtitles_online:
            any.filename = any.get_filename_srt(draft=True)
        else:
            any.filename = any.get_filename_srt(draft=False)

    show_pad = False
    if my_talk.link_to_writable_pad[0:1] != "#":
        show_pad = True

    datetime_min = datetime.datetime.min

    return render(request, "talk.html",
                  {"talk" : my_talk,
                    "subtitles": my_subtitles,
                    "page_sub_titles": my_talk.page_sub_titles,
                    "talk_speakers_statistics": speakers_in_talk_statistics,
                    "show_etherpad": show_pad,
                    "request": request,
                    "datetime_min": datetime_min})


def talk_by_frab(request, frab_id):
    return redirect(get_object_or_404(Talk, frab_id_talk=frab_id),
                    permanent=True)

def talk_by_guid(request, guid):
    #return redirect(get_object_or_404(Talk, guid=guid), permanent=True)
    # Check for available talks
    my_talks = Talk.objects.filter(guid = guid)
    referer_url = request.META.get('HTTP_REFERER')
    # If no talk was returned to be shown
    if my_talks.count() == 0:
        return render(request, "talk_unavailable.html", {"talk" : None, "request": request, "referer_url": referer_url, "guid": guid}, status=418 )
    # If the talk is in the database but not visible for whatever reasons
    elif my_talks[0].unlisted == True:
        subtitles = Subtitle.objects.filter(talk = my_talks[0])
        #guid = guid
        #referer_url = request.META.get('HTTP_REFERER')
        return render(request, "talk_unavailable.html", {"talk" : my_talks[0], "request": request, "referer_url": referer_url, "guid": guid, "subtitles": subtitles}, status=418)
    # If a talk is returned and it is currently visible
    else:
        return redirect(get_object_or_404(Talk, guid=guid), permanent=True)



def talk_by_subtitle(request, id):
    subtitle = get_object_or_404(Subtitle, pk=id)
    return redirect(subtitle.talk, permanent=True)


def updateSubtitle(request, id):
    my_obj = get_object_or_404(Subtitle, pk=id)

    form = SubtitleForm(request.POST or None, instance=my_obj)
    # quick finish btn
    if 'quick_finish_btn' in request.POST:
        talk = my_obj.talk
        #finish current step
        if my_obj.transcription_in_progress:
            # transcribing done
            my_obj.time_processed_transcribing = talk.video_duration
            my_obj.state_id = 4 # Do not touch
            my_obj.notify_subtitle_needs_timing = True
            my_obj.blocked = True
        elif my_obj.syncing_in_progress:
            # Syncing is done - if manually
            my_obj.time_processed_syncing = talk.video_duration
            my_obj.state_id = 7 # Quality check done until
        elif my_obj.quality_check_in_progress:
            # quality_check done
            my_obj.time_quality_check_done = talk.video_duration
            my_obj.state_id = 8 # Done
            # Execute Python Skript for Amara Sync in the Background?!
        elif my_obj.translation_in_progress:  # Translation
            my_obj.time_processed_translating = talk.video_duration
            my_obj.state_id = 12 # Translation finished
            # Execute Python Skript for Amara Sync in the Background?!

        my_obj.save()
        messages.add_message(request, messages.INFO, 'Step finished.')
        return redirect('talk', id=talk.pk)
    elif form.is_valid():
        form.save()
        # do stuff
        my_obj.save()
        messages.add_message(request, messages.INFO, 'Subtitle Status is saved.')
        return redirect('talk', id=my_obj.talk.pk)
    else:
        messages.add_message(request, messages.WARNING, 'You entered invalid data.')
        return redirect('talk', id=my_obj.talk.pk)


def eventStatus(request, event):
    return render(request, 'status', {'eventname':event})


# Speaker summary website
def speaker(request, speaker_id):
    # Check if the Speaker ID exists, if not return a 404
    my_speaker = get_object_or_404(Speaker, pk = speaker_id)
    # If the speaker has an doppelgaenger, do a redirect to this site
    if my_speaker.doppelgaenger_of is not None :
        return redirect('speaker', speaker_id = my_speaker.doppelgaenger_of.id)

    my_talk_persons = Talk_Persons.objects.filter(speaker = my_speaker).order_by("-talk__date").select_related('talk', 'speaker').prefetch_related('talk__subtitle_set')

    my_speakers_statistics = Statistics_Speaker.objects.filter(speaker = my_speaker) \
        .exclude(average_wpm = None, average_spm = None) \
        .order_by("language__language_en")

    # Get all languages and events the speaker participated in and create a nice looking string
    my_events_dict = {}
    my_languages_dict = {}
    my_tracks_dict = {}
    for any in my_talk_persons:
        # Every Event in which the speaker had a talk
        if any.talk.event.title in my_events_dict:
            pass
        else:
            my_events_dict[any.talk.event.title] = 0
        # Every Language the Speaker spoke in talks
        if any.talk.orig_language.display_name in my_languages_dict:
            pass
        else:
            my_languages_dict[any.talk.orig_language.display_name] = 0
        if any.talk.track.track in my_tracks_dict:
            pass
        else:
            my_tracks_dict[any.talk.track.track] = 0

    # Get all events the speaker has been to and convert to a string with commas
    first_flag = True
    my_events = ""
    for any in my_events_dict.keys():
        if first_flag:
            my_events += any
            first_flag = False
        else:
            my_events += ", " + any

    # All tracks the speaker spoke in
    my_tracks = ""
    first_flag = True
    for any in my_tracks_dict.keys():
        if first_flag:
            my_tracks += any
            first_flag = False
        else:
            my_tracks += ", " + any

    # Get all languages the speaker spoke in and convert to a string with commas
    first_flag = True
    my_languages = ""
    for any in my_languages_dict.keys():
        if first_flag:
            my_languages += any
            first_flag = False
        else:
            my_languages += ", " + any

    # Get all non unlisted talks from the speaker
    my_talks = my_speaker.talk_set.all()
    my_talks = my_talks.filter(unlisted = False).order_by("-date").prefetch_related("talk_persons_set")

    # Create talk_chunks of 3 per line
    talks_per_line = 3
    my_talks_chunk = [my_talks[x:x+talks_per_line] for x in range(0, my_talks.count(), talks_per_line)]

    # Progress Bar data
    my_speaker.__dict__.update(progress_bar_for_talks(my_talks))


    return render(request, "speaker.html", {"speaker" : my_speaker,
        "speaker_statistics" : my_speakers_statistics,
        "speakers_events" : my_events,
        "speakers_languages" : my_languages,
        "talks_chunk" : my_talks_chunk,
        "page_sub_titles": my_speaker.page_sub_titles,
        "speakers_tracks" : my_tracks,
        "request": request} )

def eventCSS(request, event):
    return render(request, "css/{}".format(event.lower()))

def eventLogo(request, event):
    return

def clock(request):#,event):
    # ...
    return HttpResponse("Hello, world!")
    """now = datetime.datetime.now()
    html = "<html><body>It is now "+str(now)+".</body></html>"
    return HttpResponse(html)"""

# Convert datetime.time into seconds
def seconds(sometime):
    return_value = 0
    return_value += ( int(sometime.strftime("%H")) * 60 * 60 +
                    int(sometime.strftime("%M")) * 60 +
                    int(sometime.strftime("%S")) )
    return return_value

# Functions for the progress bars
def _progress_bar(total, green=0.0, orange=0.0, red=0.0, precision=1):
    if total == 0:
        total = 1               # prevent division by zero

    scale = 100.0 / total
    green_amount = round(green * scale, precision)
    orange_amount = round(min(orange * scale, 100.0 - green_amount), precision)
    red_amount = round(min(red * scale,
                           100.0 - orange_amount - green_amount), precision)
    colored_amount = green_amount + orange_amount + red_amount
    grey_amount = round(100.0 - colored_amount, precision)

    return {'bar_checked': green_amount,
            'bar_synced': orange_amount,
            'bar_transcribed': red_amount,
            'bar_nothing': grey_amount,
            }

def progress_bar_for_talks(talks):
    transcribed = synced = checked = 0
    total = sum([seconds(talk.video_duration) for talk in talks])
    subtitles = Subtitle.objects.filter(is_original_lang=True,
                                        talk_id__in=[talk.id for talk in talks])
    for sub in subtitles:
        just_checked = seconds(sub.time_quality_check_done)
        just_synced = max(0, seconds(sub.time_processed_syncing) -
                          just_checked)
        just_transcribed = max(0, seconds(sub.time_processed_transcribing) -
                               just_checked - just_synced)

        transcribed += just_transcribed
        synced += just_synced
        checked += just_checked

    return _progress_bar(total,
                         green=checked,
                         orange=synced,
                         red=transcribed)

# Statistics of talks
def statistics_talks(request):
    my_talks = Talk.objects.all().exclude(average_wpm = None).order_by("-average_spm")
    return render(request, "statistics_talks.html",
        {"talks" : my_talks})

# Statistics of speakers
def statistics_speakers(request):
    my_statistics_speakers = Statistics_Speaker.objects.all().exclude(average_wpm = None).order_by("-average_spm")
    return render(request, "statistics_speakers.html",
        {"statistics_speakers" : my_statistics_speakers})

# Statistics of speakers in talks
def statistics_speakers_in_talks(request):
    my_talk_persons = Talk_Persons.objects.all().exclude(average_wpm = None).order_by("-average_spm")
    return render(request, "statistics_speakers_in_talks.html",
        {"talk_persons" : my_talk_persons})


@login_required
def text_transforms_dwim(request, subtitle_id, next_ids=None):
    TRINT = 0
    TIMING = 1
    SBV = 2

    STEPS = {TRINT: 'Convert trint transcript to pad',
             TIMING: 'Convert pad to timing input',
             SBV: 'Fix SBV linebreaks',
             }

    if next_ids is None:
        next_ids = ''

    nexts = next_ids.split(',')
    first = nexts[0]
    rest = nexts[1:]

    subtitle = get_object_or_404(Subtitle, pk=subtitle_id)
    args = {'next_ids': next_ids,
            'subtitle': subtitle,
            'first': first,
            'rest': rest,
            'form': SimplePasteForm(),
            'talk': subtitle.talk,
            }

    if (subtitle.autotiming_step == 0 and
        subtitle.transcription_in_progress and
        (subtitle.talk.has_transcript_by_trint or
         subtitle.talk.has_transcript_by_youtube)):
        args['step'] = TRINT
    elif (subtitle.autotiming_step == 0 and
          not subtitle.transcription_in_progress):
        args['step'] = TIMING
    else:
        args['step'] = SBV
        args['otherform'] = SimplePasteForm(prefix='SBV')

    args['workflow_step'] = STEPS[args['step']]

    if subtitle.talk.has_transcript_by_youtube:
        args['workflow_step'] = args['workflow_step'].replace('trint',
                                                              'youtube')

    if first:
        next_subtitle = get_object_or_404(Subtitle, pk=first)
        args['next_title'] = next_subtitle.title

    result = None
    if request.method == 'POST':
        form = SimplePasteForm(request.POST)
        if form.is_valid():
            args['form'] = form

            input = form.cleaned_data['text']

            if args['step'] == TRINT:
                if subtitle.talk.has_transcript_by_trint:
                    result = transforms.pad_from_trint(input)
                elif subtitle.talk.has_transcript_by_youtube:
                    result = transforms.pad_from_youtube(input)
                #subtitle.autotiming_step = TIMING
                subtitle.save()
            elif args['step'] == TIMING:
                result = transforms.timing_from_pad(input)
                subtitle.autotiming_step = SBV
                subtitle.save()
            elif args['step'] == SBV:
                otherform = SimplePasteForm(request.POST, prefix='SBV')

                if otherform.is_valid():
                    # result = transforms.fix_sbv_linebreaks(input,
                    #                                        otherform.cleaned_data['text'])
                    result = transforms.align_transcript_sbv(input,
                                                             otherform.cleaned_data['text'])

            args['result'] = result
            return render(request, 'transforms_result.html',
                          args)

    return render(request, 'transforms.html',
                  args)

# Export for media.ccc.de
def media_export(request, timestamp=None, *argh, **kwargs):
    #my_search_date = dateutil.parser.parse(timestamp)
    data = None
    try:
        data = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        data = None
    if data == None:
        try:
            data = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        except:
            data = None

    # Get all subtitles datasets if no date was given
    if data == None:
        my_subtitles = Subtitle.objects.all().exclude(revision=0).order_by("touched")
        #my_subtitles = Subtitle.objects.all().exclude(revision=0).exclude(revision=1).order_by("last_changed_on_amara")
    elif data != None:
        # Make data timezone aware, else the filter will fail
        data = data.replace(tzinfo=timezone.utc)
        my_subtitles = Subtitle.objects.filter(touched__gt = data).exclude(revision=0).order_by("touched")
        #my_subtitles = Subtitle.objects.filter(touched__gt = data).exclude(revision=0).exclude(revision=1).order_by("last_changed_on_amara")

    counter = my_subtitles.count()

    activity_data = {}

    csv_output = ""
    csv_output += "touched;GUID;complete;media_language;srt_language;last_changed_on_amara;revision;url;amara_key;amara_language;state;released_as_draft;c3subtitles_url;draft_source\n"

    for any in my_subtitles:
        # If the Subtitle is in quality control state and a draft is released
        if any.state_id == 7:
            csv_output += any.touched.strftime("%Y-%m-%dT%H:%M:%SZ")+";"\
                +any.talk.guid+";"\
                +str(any.complete)+";"\
                +any.language.lang_code_media+";"\
                +any.language.lang_short_srt+";"\
                +any.last_changed_on_amara.strftime("%Y-%m-%dT%H:%M:%SZ")+";"\
                +str(any.revision)\
                +";https://mirror.selfnet.de/c3subtitles/"\
                +any.talk.event.subfolder_in_sync_folder + "/"\
                +any.get_filename_srt(draft=True) +";"\
                +any.talk.amara_key+";"\
                +any.language.lang_amara_short+";"\
                +str(any.state_id)+";"\
                +str(True)\
                +";https://c3subtitles.de/talk/"\
                +str(any.talk.id)\
                + ";"\
                +"\n"
        # If the Subtitle is in transcribing or auto timing and has a
        # subtitle file from e.g. trint or youtube
        elif (any.state_id == 2 or any.state_id == 4) and any.is_original_lang and any.has_draft_subtitle_file:
            csv_output += any.touched.strftime("%Y-%m-%dT%H:%M:%SZ")+";"\
                +any.talk.guid+";"\
                +str(any.complete)+";"\
                +any.language.lang_code_media+";"\
                +any.language.lang_short_srt+";"\
                +any.last_changed_on_amara.strftime("%Y-%m-%dT%H:%M:%SZ")+";"\
                +str(any.revision)\
                +";https://mirror.selfnet.de/c3subtitles/"\
                +any.talk.event.subfolder_in_sync_folder + "/"\
                +any.get_filename_srt(draft=True) +";"\
                +any.talk.amara_key+";"\
                +any.language.lang_amara_short+";"\
                +str(any.state_id)+";"\
                +str(True)\
                +";https://c3subtitles.de/talk/"\
                +str(any.talk.id)\
                +";" + str(any.talk.transcript_by)\
                +"\n"
        else:
            csv_output += any.touched.strftime("%Y-%m-%dT%H:%M:%SZ")+";"\
                +any.talk.guid+";"\
                +str(any.complete)+";"\
                +any.language.lang_code_media+";"\
                +any.language.lang_short_srt+";"\
                +any.last_changed_on_amara.strftime("%Y-%m-%dT%H:%M:%SZ")+";"\
                +str(any.revision)\
                +";https://mirror.selfnet.de/c3subtitles/"\
                +any.talk.event.subfolder_in_sync_folder+ "/" \
                +any.get_filename_srt(draft=False)+";"\
                +any.talk.amara_key+";"\
                +any.language.lang_amara_short+";"\
                +str(any.state_id)+";"\
                + str(False)\
                +";https://c3subtitles.de/talk/"\
                +str(any.talk.id)\
                + ";"\
                + "\n"

    #return render(request, 'www/b_test.html', {"data":data})
    #return render(request, "www/raw_csv.html", {"data":csv_output})
    return HttpResponse(csv_output, content_type='text/csv')

# Dashboard
def dashboard(request):
    # LEFT COLUMN
    # Talks which need timing
    subtitles_needing_timing = Subtitle.objects.filter(talk__unlisted=False, blocked = True).order_by("-talk")

    # Talks without statistics data
    talks_one_speaker_no_statistics = []
    talks_several_speakers_no_statistics = []
    my_subtitles = Subtitle.objects.filter(is_original_lang = True).exclude(state_id = 2).order_by("-talk")
    my_subtitles = my_subtitles.exclude(state_id = 1)
    my_subtitles = my_subtitles.exclude(state_id = 4)
    my_subtitles = my_subtitles.exclude(state_id = 9)
    my_subtitles = my_subtitles.exclude(state_id = 11)
    my_subtitles = my_subtitles.exclude(state_id = 12)
    for any in my_subtitles:
        my_statistics_data = Statistics_Raw_Data.objects.filter(talk=any.talk)
        my_speakers = Talk_Persons.objects.filter(talk=any.talk)
        if my_statistics_data.count() < 1:
            if my_speakers.count()==1:
                talks_one_speaker_no_statistics.append(any.talk)
            else:
                talks_several_speakers_no_statistics.append(any.talk)

    # MIDDLE COLUMN
    # Visible talks with incomplete data
    talks_visible_no_amara_key = Talk.objects.filter(unlisted = False, amara_key = "").order_by("-id")
    talks_visible_no_filename = Talk.objects.filter(unlisted = False, filename = "").order_by("-id")
    talks_visible_no_video_duration = Talk.objects.filter(unlisted = False, video_duration = "00:00:00").order_by("-id")
    talks_visible_no_cdn_link = Talk.objects.filter(unlisted = False, link_to_video_file = "").order_by("-id")
    talks_visible_no_etherpad_link = Talk.objects.filter(unlisted = False, link_to_writable_pad = "").order_by("-id")

    # Needs to be more specific only talks in transcribing or qc
    talks_needing_c3s_yt_link = []

    # Talks without c3subtitles_youtube_link
    my_subtitles = Subtitle.objects.filter(is_original_lang = True, unlisted = False, state_id= 2,talk__c3subtitles_youtube_key="").exclude(time_processed_transcribing = "00:00:00").order_by("-talk")
    #my_subtitles = my_subtitles.exclude(state_id = 1)
    #my_subtitles = my_subtitles.exclude(state_id = 4)
    #my_subtitles = my_subtitles.exclude(state_id = 9)
    #my_subtitles = my_subtitles.exclude(state_id = 11)
    #my_subtitles = my_subtitles.exclude(state_id = 12)
    #my_subtitles = my_subtitles.exclude(talk__c3subtitles_youtube_key = "")
    for any in my_subtitles:
        talks_needing_c3s_yt_link.append(any.talk)

    # Talk without c3subtitles youtube link, listed and amara link
    talks_needing_c3s_yt_link_general = []
    talks_needing_c3s_yt_link_general = my_talks = Talk.objects.filter(unlisted = False, c3subtitles_youtube_key="").exclude(amara_key="")
    #for any_talk in my_talks:
    #    talks_needing_c3s_yt_link_general.append(any_talk)

    # Talks which need a draft subtitle
    subtitles_from_talks_needing_draft_subtitle = Subtitle.objects.filter(talk__unlisted=False, has_draft_subtitle_file = False, state_id = 2).order_by("-talk")

    # RIGHT COLUMN
    talks_visible_no_amara_video_link = Talk.objects.filter(unlisted = False, primary_amara_video_link = "").order_by("-id")
    talks_visible_transcript_by_none = Talk.objects.filter(unlisted = False, transcript_by__id = 0).order_by("-id")

    talks_with_subtitles_in_video_links = []
    my_talks = Talk.objects.all().order_by("-id")
    for any_talk in my_talks:
        if "subtitles" in any_talk.link_to_video_file:
            talks_with_subtitles_in_video_links.append(any_talk)
        elif "subtitles" in any_talk.primary_amara_video_link:
            talks_with_subtitles_in_video_links.append(any_talk)

    # Events with incomplete data
    # Visible Event without releasing folder
    events_without_releasing_folder = Event.objects.filter(subfolder_in_sync_folder = "", unlisted=False)
    
    # Visible Event without hashtag
    events_without_hashtag = Event.objects.filter(hashtag = "", unlisted=False)
    
    # Event without links to find the filenames and video urls
    events_without_links_to_find_the_filenames_and_video_urls = Event.objects.filter(unlisted=False, webpages_to_find_video_links_and_filenames="")

    return render(request, "dashboard.html",
        {"talks_one_speaker_no_statistics": talks_one_speaker_no_statistics,\
        "talks_several_speakers_no_statistics": talks_several_speakers_no_statistics,\
        "talks_visible_no_amara_key": talks_visible_no_amara_key,\
        "talks_visible_no_filename": talks_visible_no_filename,\
        "talks_visible_no_video_duration": talks_visible_no_video_duration,\
        "talks_visible_no_cdn_link": talks_visible_no_cdn_link,\
        "talks_visible_no_etherpad_link": talks_visible_no_etherpad_link,\
        "talks_visible_no_amara_video_link": talks_visible_no_amara_video_link,\
        "talks_visible_transcript_by_none": talks_visible_transcript_by_none,\
        "talks_needing_c3s_yt_link": talks_needing_c3s_yt_link,\
        "talks_needing_c3s_yt_link_general": talks_needing_c3s_yt_link_general,\
        "events_without_releasing_folder": events_without_releasing_folder,\
        "events_without_hashtag": events_without_hashtag,\
        "talks_with_subtitles_in_video_links": talks_with_subtitles_in_video_links,\
        "events_without_links_to_find_the_filenames_and_video_urls": events_without_links_to_find_the_filenames_and_video_urls,\
        "subtitles_needing_timing": subtitles_needing_timing,\
        "subtitles_from_talks_needing_draft_subtitle": subtitles_from_talks_needing_draft_subtitle
        })

# Trint Webhook Receiver
def trint_webhook_receiver(request):
    trint_key = request.POST.get("transcriptId")
    trint_event = request.POST.get("eventType")
    if trint_event == "TRANSCRIPT_COMPLETE":
        my_talks = Talk.objects.filter(trint_transcript_id = trint_key)
        if my_talks.count() == 1:
            my_t = my_talks[0]
            my_t.get_trint_transcript_and_send_via_email()
    return HttpResponse(status=200)
