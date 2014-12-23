from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
from www.models import Event, Talk, Subtitle, Language
from www.forms import SubtitleForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import datetime

# Create your views here.

def start(request):
    try:
        my_events = Event.objects.all()
    except ObjectDoesNotExist:
        raise Http404

    return render(request, "www/helloworld.html", {"events" : my_events})

def event (request, event_acronym, *args, **kwargs):
    try:
        my_event = Event.objects.select_related('Event_Days','Talk','Language').get(acronym = event_acronym)
        my_talks = my_event.talk_set.filter(blacklisted = False).order_by("day",
        "date",
        "start",
        "room__room")
        my_langs = Language.objects.filter(pk__in=[a['orig_language'] for a in my_talks.values('orig_language')])
        if "day" in kwargs and int(kwargs.get("day")) > 0:
            my_talks = my_talks.filter(day__index = kwargs.pop("day"))
        if "lang" in kwargs:
            my_talks = my_talks.filter(orig_language__lang_amara_short = kwargs.pop("lang"))
    except ObjectDoesNotExist:
        raise Http404

    return render(request, "www/event.html", {"my_talks" : my_talks,
        "my_event" : my_event,
        "my_days" : my_event.event_days_set.all(),
        "my_langs" : my_langs} )


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

    if sub.time_processed_transcribing == talk.video_duration != sub.time_processed_syncing:
        return "Manuel syncing, please wait"
    if sub.time_quality_check_done == talk.video_duration:
        return "Year it's done."

    if sub.is_original_lang:
        if sub.time_processed_transcribing < talk.video_duration:
            # remove the unnecessary fields
            #form.fields.pop("time_processed_transcribing")
            form.fields.pop("time_processed_syncing")
            form.fields.pop("time_quality_check_done")
            form.fields.pop("time_processed_translating")

            #  state_en nur id 1,2,3 oder 9
            new_query = form.fields['state'].choices.queryset.filter(pk__in=[1,2,3,9])
            form.fields['state']._set_queryset(new_query)

            # add finish transcribing button
            form.quick_btn = 'Finish Transcribing'

            return form
        elif sub.time_processed_transcribing == sub.time_processed_syncing == talk.video_duration:
            # remove the unnecessary fields
            form.fields.pop("time_processed_transcribing")
            form.fields.pop("time_processed_syncing")
            #form.fields.pop("time_quality_check_done")
            form.fields.pop("time_processed_translating")

            #  state_en nur id 1,2,3 oder 9
            new_query = form.fields['state'].choices.queryset.filter(pk__in=[6,7])
            form.fields['state']._set_queryset(new_query)

            # add finish transcribing button
            form.quick_btn = 'Finish quality check'

            return form
    else: #no sub.is_original_lang
        # remove the unnecessary fields
        form.fields.pop("time_processed_transcribing")
        form.fields.pop("time_processed_syncing")
        form.fields.pop("time_quality_check_done")
        #form.fields.pop("time_processed_translating")

        #  state_en nur id 1,2,3 oder 9
        new_query = form.fields['state'].choices.queryset.filter(pk__in=[11,12])
        form.fields['state']._set_queryset(new_query)

        # add finish transcribing button
        form.quick_btn = 'Finish Translating'

        return form

    return


def talk (request, talk_id):
    try:
        my_talk = Talk.objects.get(pk=talk_id)
        my_subtitles = my_talk.subtitle_set.all().order_by("is_original_lang","language__lang_amara_short")
        for s in my_subtitles:
            s.form = get_subtitle_form(request, my_talk, s)
            # todo add ifs so that its set correct depending of the status
    except ObjectDoesNotExist:
        raise Http404

    return render(request, "www/talk.html", {"talk" : my_talk, "subtitles": my_subtitles} )




def updateSubtitle(request, subtitle_id):
    try:
        my_obj = Subtitle.objects.get(pk=subtitle_id)
    except ObjectDoesNotExist:
        raise Http404

    form = SubtitleForm(request.POST or None, instance=my_obj)

    # quick finish btn
    if 'quick_finish_btn' in request.POST:
        talk = my_obj.talk
        #finish current step
        if my_obj.is_original_lang:
            if my_obj.time_processed_transcribing < talk.video_duration:
                # transcribing
                my_obj.time_processed_transcribing = talk.video_duration
                my_obj.state_id = 3
            elif my_obj.time_processed_transcribing == my_obj.time_processed_syncing == talk.video_duration:
                # quality_check
                my_obj.time_quality_check_done = talk.video_duration
                my_obj.state_id = 8
        else: # translating
            my_obj.time_processed_translating = talk.video_duration
            my_obj.state_id = 12


        my_obj.save()
        messages.add_message(request, messages.INFO, 'Step finished.')
        return redirect('talk', talk_id=talk.pk)
    elif form.is_valid():
        form.save()
        # do stuff
        my_obj.save()
        messages.add_message(request, messages.INFO, 'Subtitle Status is saved.')
        return redirect(talk, talk_id=my_obj.talk.pk)
    else:
        messages.add_message(request, messages.WARNING, 'You entered invalid data.')
        return redirect(talk, talk_id=my_obj.talk.pk)




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
