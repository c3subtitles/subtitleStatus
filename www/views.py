from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
from www.models import Event, Talk, Subtitle, Language, Speaker, Talk_Persons, Statistics_Event, Statistics_Speaker, Event_Days
from www.forms import SubtitleForm, BForm, SimplePasteForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from www import transforms
import datetime
#from django import forms
#from copy import deepcopy
#import django_filters

# Create your views here.

# Start of the Website with all the events
def start(request):
    try:
        my_events = list(Event.objects.all().order_by("-start"))

        # Function for the progress bars
        for every_event in my_events:
            my_talks = Talk.objects.filter(event = every_event, blacklisted = False)
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

    return render(request, "www/main.html", {"events" : my_events, "request": request} )

# Overview over the Talks of one event
def event (request, event_acronym, *args, **kwargs):
    try:
        my_event = Event.objects.prefetch_related('event_days_set','talk_set').get(acronym = event_acronym)
        my_talks = my_event.talk_set.filter(blacklisted = False).order_by("day",
            "date",
            "start",
            "room__room")
        # Special case for 34c4
        if my_event.id == 6:
            my_talks = my_talks.all().exclude(video_duration = "00:00:00").exclude(amara_key = "").exclude(filename = "")
        my_langs = Language.objects.filter(pk__in=[a['orig_language'] for a in my_talks.values('orig_language')])
        if "day" in kwargs and int(kwargs.get("day")) > 0:
            day = kwargs.pop("day")
            my_talks = my_talks.filter(day__index = day)
        if "lang" in kwargs:
            lang = kwargs.pop("lang")
            my_talks = my_talks.filter(orig_language__lang_amara_short = lang)

        my_event.__dict__.update(progress_bar_for_talks(my_talks))

        for every_talk in my_talks:
            every_talk.subtitles = every_talk.subtitle_set.order_by('-is_original_lang')

        # Create cunk for the 3 columns display of talks on event page
        talks_per_line = 3
        talks_chunk = [my_talks[x:x+talks_per_line] for x in range(0, len(my_talks), talks_per_line)]

        datetime_min = datetime.datetime.min

    except ObjectDoesNotExist:
        raise Http404

    return render(request, "www/event.html", {"my_talks" : my_talks,
        "my_event" : my_event,
        "my_days" : my_event.event_days_set.all(),
        "my_langs" : my_langs,
        "page_sub_titles": my_event.page_sub_titles,
        "talks_chunk" : talks_chunk,
        "request": request,
        "datetime_min": datetime_min})

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


def talk(request, talk_id):
    my_talk = get_object_or_404(Talk, pk=talk_id, blacklisted=False)
    my_subtitles = my_talk.subtitle_set.all().order_by("-is_original_lang","language__lang_amara_short")
    for s in my_subtitles:
        s.form = get_subtitle_form(request, my_talk, s)

    speakers_in_talk_statistics = Talk_Persons.objects.filter(talk = my_talk)

    show_pad = False
    if my_talk.link_to_writable_pad[0:1] != "#":
        show_pad = True

    datetime_min = datetime.datetime.min

    return render(request, "www/talk.html",
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
    return redirect(get_object_or_404(Talk, guid=guid), permanent=True)


def talk_by_subtitle(request, subtitle_id):
    try:
        my_subtitle = Subtitle.objects.get(id = subtitle_id)
    except ObjectDoesNotExist:
        raise Http404
    my_talk = Talk.objects.filter(id = my_subtitle.talk.id)
    return redirect(get_object_or_404(my_talk), permanent=True)

def updateSubtitle(request, subtitle_id):
    try:
        my_obj = Subtitle.objects.get(pk=subtitle_id)
    except ObjectDoesNotExist:
        raise Http404

    form = SubtitleForm(request.POST or None, instance=my_obj)
    print(request.POST)
    # quick finish btn
    if 'quick_finish_btn' in request.POST:
        talk = my_obj.talk
        #finish current step
        if my_obj.transcription_in_progress:
            # transcribing done
            my_obj.time_processed_transcribing = talk.video_duration
            my_obj.state_id = 4 # Do not touch
            my_obj.needs_automatic_syncing = True
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
        return redirect('talk', talk_id=talk.pk)
    elif form.is_valid():
        form.save()
        # do stuff
        my_obj.save()
        messages.add_message(request, messages.INFO, 'Subtitle Status is saved.')
        return redirect('talk', talk_id=my_obj.talk.pk)
    else:
        messages.add_message(request, messages.WARNING, 'You entered invalid data.')
        return redirect('talk', talk_id=my_obj.talk.pk)


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

    # Get all non blacklisted talks from the speaker
    my_talks = my_speaker.talk_set.all()
    my_talks = my_talks.filter(blacklisted = False).order_by("-date").prefetch_related("talk_persons_set")

    # Create talk_chunks of 3 per line
    talks_per_line = 3
    my_talks_chunk = [my_talks[x:x+talks_per_line] for x in range(0, my_talks.count(), talks_per_line)]

    # Progress Bar data
    my_speaker.__dict__.update(progress_bar_for_talks(my_talks))


    return render(request, "www/speaker.html", {"speaker" : my_speaker,
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

    if total == 0:
        total = 1               # prevent division by zero

    return _progress_bar(total,
                         green=checked,
                         orange=synced,
                         red=transcribed)

# Statistics of talks
def statistics_talks(request):
    my_talks = Talk.objects.all().exclude(average_wpm = None).order_by("-average_spm")
    return render(request, "www/statistics_talks.html",
        {"talks" : my_talks})

# Statistics of speakers
def statistics_speakers(request):
    my_statistics_speakers = Statistics_Speaker.objects.all().exclude(average_wpm = None).order_by("-average_spm")
    return render(request, "www/statistics_speakers.html",
        {"statistics_speakers" : my_statistics_speakers})

# Statistics of speakers in talks
def statistics_speakers_in_talks(request):
    my_talk_persons = Talk_Persons.objects.all().exclude(average_wpm = None).order_by("-average_spm")
    return render(request, "www/statistics_speakers_in_talks.html",
        {"talk_persons" : my_talk_persons})

# Test-View
def test(request):

    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            sort_spm = cd.get("sort_spm")
            sort_desc = cd.get("sort_desc")
        else:
            sort_spm = False
            sort_desc = False
    else:
        sort_spm = False
        sort_desc = False
        form = TestForm()


    my_talk_persons = Talk_Persons.objects.all().exclude(average_wpm = None).order_by("-average_spm")
    my_langs = Language.objects.filter(pk__in=[a['talk__orig_language'] for a in my_talk_persons.values('talk__orig_language')])
    my_events = Event.objects.filter(pk__in=[a['talk__event'] for a in my_talk_persons.values('talk__event')])
    my_event_days = Event_Days.objects.filter(pk__in=[a['talk__day'] for a in my_talk_persons.values('talk__day')])
    event_days = {}
    for any in my_event_days:
        if any.index in event_days:
            pass
        else:
            event_days[any.index] = 0


    return render(request, "www/test.html",
        {"talk_persons" : my_talk_persons,
        "my_langs" : my_langs,
        "my_events" : my_events,
        "event_days" : event_days,
        "sort_spm" : sort_spm,
        "sort_desc" : sort_desc,
        "form" : form}
        )

# B Test-Form
def b_test(request):
    text = "Enter Data here"
     # If this is a POST request then process the Form data
    if request.method == 'POST':
        my_form = BForm(request.POST)
        if my_form.is_valid():
            text = my_form.cleaned_data["my_text"]
            """
            # Part for the questions
            # Remove double newlines
            text = text.replace("\r\n\r\n", "\r\n")
            # Replace linebreaks with spaces
            text = text.replace("\r\n", " ")
            for letter in ["A", "B", "C", "D"]:
                text = text.replace(" " + letter + ".", "\r\n" + letter + ".")
            for letter in ["i.", "ii.", "iii.", "iv.", "v."]:
                text = text.replace(" " + letter, "\r\n" + letter)
            """

            #"""
            # Part for the answers

            # Remove the lines with the broken boxes
            text = text.replace("✗\r\n","")
            # Replace double empty lines
            text = text.replace("\r\n\r\n", "\r\n")
            # Replace linebreaks with spaces
            text = text.replace("\r\n"," ")
            text = text.replace(" ☐","\r\n☐")
            text = text.replace(" •", "\r\n•")
            #"""
            counter = len(text)
            if text[counter - 1]==" ":
                text = text[0:-1]
            #my_form.my_text = text
            my_form = BForm(initial={"my_text":text,})
        else:
            #my_form.cleaned_data["my_text"] = "BÄtsch"
            text = "Bätsch"
            #text += "Ätsch!"
            #return HttpResponseRedirect(reverse(text))
     # If this is a GET (or any other method) create the default form.
    else:
        my_form = BForm()#initial={"my_text":text,})

    return render(request, "www/b_test.html",
        {
        "form" : my_form,
        "my_text": text}
        )


@login_required
def text_transforms_dwim(request, subtitle_id, next_ids):
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
        subtitle.talk.has_transcript_by_trint):
        args['step'] = TRINT
    elif (subtitle.autotiming_step == 0 and
          not subtitle.transcription_in_progress):
        args['step'] = TIMING
    elif subtitle.autotiming_step == 1:
        args['step'] = SBV
        args['otherform'] = SimplePasteForm(prefix='SBV')
    else:
        args['step'] = 2

    args['workflow_step'] = STEPS[args['step']]

    if first:
        next_subtitle = get_object_or_404(Subtitle, pk=first)
        args['next_title'] = next_subtitle.title

    result = None
    if request.method == 'POST':
        form = SimplePasteForm(request.POST)
        if form.is_valid():
            args['form'] = form

            input = form.cleaned_data['text']
            foo = subtitle.transcription_in_progress

            if args['step'] == TRINT:
                result = transforms.pad_from_trint(input)
                subtitle.autotiming_step = TIMING
                subtitle.save()
            elif args['step'] == TIMING:
                result = transforms.timing_from_pad(input)
                subtitle.autotiming_step = SBV
                subtitle.save()
            elif args['step'] == SBV:
                otherform = SimplePasteForm(request.POST, prefix='SBV')

                if otherform.is_valid():
                    result = transforms.fix_sbv_linebreaks(input,
                                                           otherform.cleaned_data['text'])

            args['result'] = result
            return render(request, 'www/transforms_result.html',
                          args)

    return render(request, 'www/transforms.html',
                  args)
