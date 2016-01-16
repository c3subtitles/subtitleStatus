from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
from www.models import Event, Talk, Subtitle, Language
from www.forms import SubtitleForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from django.contrib import messages
import datetime
#from copy import deepcopy

# Create your views here.

def start(request):
    try:
        my_events = list(Event.objects.all().order_by("-start"))     

        # Function for the progress bars
        for every_event in my_events:
            my_talks = Talk.objects.filter(event = every_event, blacklisted = False)
            every_event.__dict__.update(progress_bar_for_talks(my_talks))
    except ObjectDoesNotExist:
        raise Http404
    
    return render(request, "www/main.html", {"events" : my_events} )

def event (request, event_acronym, *args, **kwargs):
    try:
        my_event = Event.objects.select_related('Event_Days','Talk','Language','Subtitle','Rooms').get(acronym = event_acronym)
        my_talks = my_event.talk_set.filter(blacklisted = False).order_by("day",
        "date",
        "start",
        "room__room")
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
        
    except ObjectDoesNotExist:
        raise Http404

    return render(request, "www/event.html", {"my_talks" : my_talks,
        "my_event" : my_event,
        "my_days" : my_event.event_days_set.all(),
        "my_langs" : my_langs,
        "talks_chunk" : talks_chunk} )


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

    if sub.is_original_lang:
        if sub.state_id == 2:      # still transcribing
            # remove the unnecessary fields
            #form.fields.pop("time_processed_transcribing")
            form.fields.pop("time_processed_syncing")
            form.fields.pop("time_quality_check_done")
            form.fields.pop("time_processed_translating")

            # add finish transcribing button
            form.quick_btn = 'Finish Transcribing'

            return form
        elif sub.state_id == 7:    # in quality control
            # remove the unnecessary fields
            form.fields.pop("time_processed_transcribing")
            form.fields.pop("time_processed_syncing")
            #form.fields.pop("time_quality_check_done")
            form.fields.pop("time_processed_translating")

            # add finish transcribing button
            form.quick_btn = 'Finish quality check'

            return form
    else: #no sub.is_original_lang
        if sub.state_id == 11:     # in translation
            # remove the unnecessary fields
            form.fields.pop("time_processed_transcribing")
            form.fields.pop("time_processed_syncing")
            form.fields.pop("time_quality_check_done")
            #form.fields.pop("time_processed_translating")

            # add finish transcribing button
            form.quick_btn = 'Finish Translating'

            return form

    return


def talk (request, talk_id):
    try:
        my_talk = Talk.objects.get(pk=talk_id)
        my_subtitles = my_talk.subtitle_set.all().order_by("-is_original_lang","language__lang_amara_short")
        for s in my_subtitles:
            s.form = get_subtitle_form(request, my_talk, s)
            # todo add ifs so that its set correct depending of the status
            #?!
    except ObjectDoesNotExist:
        raise Http404

    return render(request, "www/talk.html", {"talk" : my_talk, "subtitles": my_subtitles} )




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
        if my_obj.is_original_lang:
            if my_obj.state_id == 2:
                # transcribing done
                my_obj.time_processed_transcribing = talk.video_duration
                my_obj.state_id = 4 # Do not touch
                my_obj.needs_automatic_syncing = True
                my_obj.blocked = True
            elif my_obj.state_id == 5:
                # Syncing is done - if manually
                my_obj.time_processed_syncing = talk.video_duration
                my_obj.state_id = 7 # Quality check done until
            elif my_obj.state_id == 7:
                # quality_check done
                my_obj.time_quality_check_done = talk.video_duration
                my_obj.state_id = 8 # Done
                # Execute Python Skript for Amara Sync in the Background?!
        elif my_obj.state_id == 11:  # Translation
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

def speaker(request, event):
    return render(request, 'status', {'eventname':event})

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
        transcribed += seconds(sub.time_processed_transcribing)
        synced += seconds(sub.time_processed_syncing)
        checked += seconds(sub.time_quality_check_done)

    if total == 0:
        total = 1               # prevent division by zero

    return _progress_bar(total,
                         green=checked,
                         orange=synced,
                         red=transcribed)
