from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.shortcuts import get_object_or_404
from django.utils.html import format_html

from www.models import Talk
from www.models import Tracks
from www.models import Links
from www.models import Type_of
from www.models import Speaker
from www.models import Subtitle
from www.models import States
from www.models import Event
from www.models import Event_Days
from www.models import Rooms
from www.models import Language
from www.models import Statistics_Raw_Data
from www.models import Statistics_Speaker
from www.models import Statistics_Event
from www.models import Talk_Persons
from www.models import Transcript


# Register your models here.

class DayIndexFilter(admin.SimpleListFilter):
    title = 'Day'
    parameter_name = 'day'

    def lookups(self, request, model_admin):
        indexes = {day.index for day in Event_Days.objects.all()}

        return ((index, 'Day {}'.format(index))
                for index in sorted(indexes))

    def queryset(self, request, queryset):
        index = self.value()

        if index is not None:
            return queryset.filter(day__index=index)
        else:
            return queryset

class HasVideoLinkFilter(admin.SimpleListFilter):
    title = 'Has link to video file'
    parameter_name = 'link_to_video_file'

    def lookups(self, request, model_admin):
        return (('yes', 'Yes'),
                ('no', 'No'),
        )

    def queryset(self, request, queryset):
        ans = self.value()

        if ans == "no":
            return queryset.filter(link_to_video_file = "")
        elif ans == "yes":
            return queryset.all().exclude(link_to_video_file = "")
        else:
            return queryset

class HasAmaraKeyFilter(admin.SimpleListFilter):
    title = 'Has amara key'
    parameter_name = 'amara_key'

    def lookups(self, request, model_admin):
        return (('yes', 'Yes'),
                ('no', 'No'),
        )

    def queryset(self, request, queryset):
        ans = self.value()

        if ans == "no":
            return queryset.filter(amara_key = "")
        elif ans == "yes":
            return queryset.all().exclude(amara_key = "")
        else:
            return queryset

class HasFilenameFilter(admin.SimpleListFilter):
    title = 'Has filename'
    parameter_name = 'filename'

    def lookups(self, request, model_admin):
        return (('yes', 'Yes'),
                ('no', 'No'),
        )

    def queryset(self, request, queryset):
        ans = self.value()

        if ans == "no":
            return queryset.filter(filename = "")
        elif ans == "yes":
            return queryset.all().exclude(filename = "")
        else:
            return queryset

class HasVideoDurationFilter(admin.SimpleListFilter):
    title = 'Has video duration'
    parameter_name = 'video_duration'

    def lookups(self, request, model_admin):
        return (('yes', 'Yes'),
                ('no', 'No'),
        )

    def queryset(self, request, queryset):
        ans = self.value()

        if ans == "no":
            return queryset.filter(video_duration__hour=0, video_duration__minute=0, video_duration__second=0)
        elif ans == "yes":
            return queryset.all().exclude(video_duration__hour=0, video_duration__minute=0, video_duration__second=0)
        else:
            return queryset

class HasC3SubtitlesYTKeyFilter(admin.SimpleListFilter):
    title = 'Has c3subtitles YT key'
    parameter_name = 'c3subtitles_youtube_key'

    def lookups(self, request, model_admin):
        return (('yes', 'Yes'),
                ('no', 'No'),
        )

    def queryset(self, request, queryset):
        ans = self.value()

        if ans == "no":
            return queryset.filter(c3subtitles_youtube_key = "")
        elif ans == "yes":
            return queryset.all().exclude(c3subtitles_youtube_key = "")
        else:
            return queryset

class HasTrintTranscriptKeyFilter(admin.SimpleListFilter):
    title = 'Has Trint Transcript Key'
    parameter_name = 'trint_transcript_id'

    def lookups(self, request, model_admin):
        return (('yes', 'Yes'),
                ('no', 'No'),
        )

    def queryset(self, request, queryset):
        ans = self.value()

        if ans == "no":
            return queryset.filter(trint_transcript_id = "")
        elif ans == "yes":
            return queryset.all().exclude(trint_transcript_id = "")
        else:
            return queryset

@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    def video_duration_formated(self, obj):
        return obj.video_duration.strftime("%H:%M:%S h")

    video_duration_formated.short_description = "Video Duration"

    def get_trint_transcript_via_email(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        for sid in selected:
            talk = get_object_or_404(Talk, pk=sid)
            talk.get_trint_transcript_and_send_via_email()

    get_trint_transcript_via_email.short_description = "Trint: Get a trint transcript via email (check if the dataset now has a trint key)"

    def get_trint_transcript_no_email(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        for sid in selected:
            talk = get_object_or_404(Talk, pk=sid)
            talk.get_trint_transcript_and_send_via_email(do_send_email=False)

    get_trint_transcript_no_email.short_description = "Trint: Get a trint transcript but NO email (check if the dataset now has a trint key)"

    def create_amara_key(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            talk = get_object_or_404(Talk, pk=sid)
            talk.create_amara_key()

    create_amara_key.short_description = (
        "Amara: Create amara key and store it in the db, use the primary_video_link"
    )

    def import_video_links_from_amara(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            talk = get_object_or_404(Talk, pk=sid)
            talk.get_video_links_from_amara(do_save=True)

    import_video_links_from_amara.short_description = (
        "Amara: Import video links from amara into the c3subtitles db"
    )

    def set_talk_original_language_as_primary_audio_language_on_amara(
        self, request, queryset
    ):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            talk = get_object_or_404(Talk, pk=sid)
            talk.make_talk_language_primary_on_amara(force_amara_update=True)

    set_talk_original_language_as_primary_audio_language_on_amara.short_description = (
        "Amara: Make the talk language the primary audio language on amara"
    )

    def complete_amara_link_update(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            talk = get_object_or_404(Talk, pk=sid)
            talk.update_video_links_in_amara()

    complete_amara_link_update.short_description = (
        "Amara: Complete Link Update from db to amara"
    )

    def upload_first_subtitle_orig_lang_with_disclaimer(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            talk = get_object_or_404(Talk, pk=sid)
            talk.upload_first_subtitle_to_amara_with_disclaimer(set_first_language=True)

    upload_first_subtitle_orig_lang_with_disclaimer.short_description = "Amara: Upload a subtitle text in the talk original language with the disclaimers to not start in amara"

    def notify_transcript_available(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            talk = get_object_or_404(Talk, pk=sid)
            talk.do_notify_transcript_available()

    notify_transcript_available.short_description = (
        "Notify: Publish messages that the transcript of this talk is available"
    )

    def amara_key_link(self, obj):
        return format_html(
            "<a href={url}>{amara_key}</a>",
            amara_key=obj.amara_key,
            url="https://amara.org/videos/" + obj.amara_key,
        )

    amara_key_link.short_description = "amara link"

    def c3s_yt_studio_link(self, obj):
        return format_html(
            "<a href={url}>{c3s_yt_key}</a>",
            c3s_yt_key=obj.c3subtitles_youtube_key,
            url="https://studio.youtube.com/video/"
            + obj.c3subtitles_youtube_key
            + "/edit",
        )

    c3s_yt_studio_link.short_description = "C3S YT Studio Link"

    def c3s_yt_link(self, obj):
        return format_html(
            "<a href={url}>{c3s_yt_key}</a>",
            c3s_yt_key=obj.c3subtitles_youtube_key,
            url="https://youtu.be/" + obj.c3subtitles_youtube_key,
        )

    c3s_yt_link.short_description = "C3S YT Link"

    def video_file_link(self, obj):
        return format_html(
            "<a href={url}>{video_link}</a>",
            video_link=obj.link_to_video_file,
            url=obj.link_to_video_file,
        )
    
    video_file_link.short_description = "Video Link"

    def link_to_pad(self, obj):
        return format_html(
            "<a href={url}>{pad_link}</a>",
            pad_link=obj.link_to_writable_pad,
            url=obj.link_to_writable_pad,
        )
    
    link_to_pad.short_description = "Etherpad"

    actions = [
        "create_amara_key",
        "import_video_links_from_amara",
        "set_talk_original_language_as_primary_audio_language_on_amara",
        "upload_first_subtitle_orig_lang_with_disclaimer",
        "complete_amara_link_update",
        "get_trint_transcript_via_email",
        "get_trint_transcript_no_email",
        "notify_transcript_available",
    ]
    date_hierarchy = "date"
    list_display = (
        "id",
        "frab_id_talk",
        "title",
        "event",
        "room",
        "day",
        "start",
        "unlisted",
        "transcript_by",
        "orig_language",
        "link_to_pad",
        "video_file_link",
        "amara_key",
        "amara_key_link",
        "c3subtitles_youtube_key",
        "c3s_yt_studio_link",
        "c3s_yt_link",
        "video_duration_formated",
        "filename",
        "needs_complete_amara_update",
        "recalculate_talk_statistics",
        "recalculate_speakers_statistics",
        "has_priority",
        "primary_amara_video_link",
        "additional_amara_video_links",
        "internal_comment",
        "trint_transcript_id",
    )
    list_filter = (
        "event",
        DayIndexFilter,
        "room",
        "recalculate_talk_statistics",
        "unlisted",
        HasVideoLinkFilter,
        HasAmaraKeyFilter,
        HasFilenameFilter,
        HasVideoDurationFilter,
        HasC3SubtitlesYTKeyFilter,
        "transcript_by",
        HasTrintTranscriptKeyFilter,
    )
    search_fields = (
        "title",
        "event__acronym",
        "frab_id_talk",
        "id",
    )
    ordering = (
        "-event",
        "date",
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('id', 'acronym', 'title', 'start', 'days', 'city', 'building',)
    list_filter = ('city',)
    ordering = ('-id',)


@admin.register(Event_Days)
class EventDaysAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('id', 'event', 'index', 'date', 'day_start', 'day_end', )
    list_filter = ('index', 'event__acronym',)


class LanguageFilter(admin.SimpleListFilter):
    title = 'Language'
    parameter_name = 'language'


    def lookups(self, request, model_admin):
        return (('en', 'English'),
                ('de', 'German'),
                ('tlh', 'Klingon'),
        )

    def queryset(self, request, queryset):
        lang = self.value()

        if lang is not None:
            return queryset.filter(language__lang_amara_short=self.value())
        else:
            return queryset


class WorkflowFilter(admin.SimpleListFilter):
    title = 'Needs Interaction'
    parameter_name = 'workflow'

    def lookups(self, request, model_admin):
        return (('yes', 'Needs interaction'),
                #('new', 'Needs a transcript'),
                ('no', 'Does not need interaction'))

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        elif self.value() == 'yes':
            return queryset.filter(state=4).exclude(unlisted=True)
        # elif self.value() == 'new':
        #     return queryset.filter(talk__transcript_by=None).exclude(unlisted=True)
        else:
            return queryset.exclude(state=4)

class HasDraftSubtitleFileFilter(admin.SimpleListFilter):
    title = 'Has Draft Subtitle File'
    parameter_name = 'draft_subtitle_file'

    def lookups(self, request, model_admin):
        return (('yes', 'Yes'),
                ('no', 'No'),
        )

    def queryset(self, request, queryset):
        ans = self.value()

        if ans == "no":
            return queryset.filter(has_draft_subtitle_file = False)
        elif ans == "yes":
            return queryset.filter(has_draft_subtitle_file = True)
        else:
            return queryset


@admin.register(Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    def status(self, obj):
        stamp = None

        if obj.transcription_in_progress:
            stamp = obj.time_processed_transcribing
        elif obj.syncing_in_progress:
            stamp = obj.time_processed_syncing
        elif obj.quality_check_in_progress:
            stamp = obj.time_quality_check_done
        elif obj.translation_in_progress:
            stamp = obj.time_processed_translating

        if stamp:
            return "{} {}".format(obj.state, stamp)
        else:
            return obj.state

    def talk_id_link(self, obj):
        tid = obj.talk_id

        return format_html(
            "<a href={url}>{talk_id}</a>", talk_id=tid, url=reverse("talk", args=[tid])
        )

    talk_id_link.short_description = "talk id"

    def talk_frab_id(self, obj):
        return obj.talk.frab_id_talk

    talk_frab_id.short_description = "frab id"

    def amara_key_link(self, obj):
        return format_html(
            "<a href={url}>{amara_key}</a>",
            amara_key=obj.talk.amara_key,
            url="https://amara.org/videos/" + obj.talk.amara_key,
        )

    amara_key_link.short_description = "amara link"

    def reset_to_pad(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            subtitle = get_object_or_404(Subtitle, pk=sid)
            subtitle.autotiming_step = 0
            subtitle.save()

    reset_to_pad.short_description = "Restart Workflow from Pad-from-Trint"

    def reset_to_timing(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            subtitle = get_object_or_404(Subtitle, pk=sid)
            subtitle.autotiming_step = 0
            subtitle.set_to_autotiming_in_progress()
            subtitle.save()

    reset_to_timing.short_description = "Restart Workflow from Timing-from-Pad"

    def reset_to_sbv(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            subtitle = get_object_or_404(Subtitle, pk=sid)
            subtitle.autotiming_step = 2
            subtitle.save()

    reset_to_sbv.short_description = "Restart Workflow from Fix-SBV"

    def reset_to_transcribing(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            subtitle = get_object_or_404(Subtitle, pk=sid)
            subtitle.reset_from_complete()

    reset_to_transcribing.short_description = "Reset subtitle to transcribing"

    def reset_to_qc(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        for sid in selected:
            subt = get_object_or_404(Subtitle, pk=sid)
            if subt.is_original_lang:
                my_talk = Talk.objects.get(id=subt.talk_id)
                subt.time_processed_transcribing = my_talk.video_duration
                subt.time_processed_syncing = my_talk.video_duration
                subt.notify_subtitle_needs_timing = False
                subt.blocked = False
                subt.state_id = 7  # Quality control done until
                subt.notify_subtitle_ready_for_quality_control = True
                subt.draft_needs_sync_to_sync_folder = True  # Release the draft
                subt.has_draft_subtitle_file = False
                subt.save()
                # Let the related statistics be calculated
                subt.talk.reset_related_statistics_data()

    reset_to_qc.short_description = "Set subtitle to Quality Control"

    def transforms_dwim(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)

        ids = [
            subtitle.pk
            for subtitle in Subtitle.objects.filter(pk__in=selected).order_by(
                "autotiming_step"
            )
        ]

        first = ids[0]
        rest = ",".join(ids[1:])
        return HttpResponseRedirect(reverse("workflowTransforms", args=[first, rest]))

    transforms_dwim.short_description = "Do-What-I-Mean (Text Transformation)"

    actions = [
        "transforms_dwim",
        "reset_to_transcribing",
        "reset_to_pad",
        "reset_to_timing",
        "reset_to_sbv",
        "reset_to_qc",
    ]
    list_display = (
        "id",
        "talk_id_link",
        "talk_frab_id",
        "amara_key_link",
        "talk",
        "language",
        "is_original_lang",
        "status",
        "complete",
        "unlisted",
        "touched",
    )
    list_filter = (
        WorkflowFilter,
        LanguageFilter,
        "is_original_lang",
        "state",
        "complete",
        "unlisted",
        HasDraftSubtitleFileFilter,
    )
    raw_id_fields = ("talk",)
    search_fields = (
        "talk__event__acronym",
        "talk__title",
        "talk__frab_id_talk",
        "id",
        "talk__subtitle_talk",
        "talk__id",
    )



@admin.register(States)
class StatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_en',)
    ordering = ('id',)


@admin.register(Talk_Persons)
class TalkPersonsAdmin(admin.ModelAdmin):
    def average_wpm_formated(self, obj):
        try:
            return format(obj.average_wpm, ".1f")
        except:
            return "-"
    average_wpm_formated.short_description = "avg wpm"

    def average_spm_formated(self, obj):
        try:
            return format(obj.average_spm, ".1f")
        except:
            return "-"
    average_spm_formated.short_description = "avg spm"


    #date_hierarchy = 'id'
    list_display = ('id', 'speaker_id', 'speaker', 'talk_id', 'talk', 'created', 'touched', 'average_wpm_formated',
                    'average_spm_formated', 'recalculate_statistics', 'strokes', 'time_delta', 'n_most_frequent_words',)
    #list_filter = ()
    search_fields = ('id', 'talk__title', 'speaker__name', 'talk__id', 'speaker__id', )
    ordering = ('-id', )


@admin.register(Statistics_Raw_Data)
class StatisticsRawDataAdmin(admin.ModelAdmin):
    def speakerid(self, obj):
        return str(obj.speaker_id)
    speakerid.short_description = "Sp ID"

    def talkid(self, obj):
        return str(obj.talk_id)
    talkid.short_description = "Tk ID"

    def start_formated(self, obj):
        return obj.start.strftime("%H:%M:%S.%f")
    start_formated.short_description = "Start"

    def end_formated(self, obj):
        return obj.end.strftime("%H:%M:%S.%f")
    end_formated.short_description = "End"

    list_display = ('id', 'speakerid', 'speaker', 'talkid', 'talk', 'recalculate_statistics', 'start_formated', 'end_formated', 'time_delta', 'words', 'strokes',)
    search_fields = ('id', 'talk__title', 'speaker__name', 'talk__id', 'speaker__id', )
    ordering = ('-id',)
    raw_id_fields = ('speaker', 'talk',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'language_en', 'language_de', 'lang_amara_short', 'lang_short_srt', 'amara_order', 'lang_code_media', 'lang_code_iso_639_1',)
    search_fields = ('language_en', 'language_de', 'lang_amara_short', 'lang_short_srt', 'amara_order', 'lang_code_media', 'lang_code_iso_639_1',)
    ordering = ('-id',)


@admin.register(Links)
class LinksAdmin(admin.ModelAdmin):
    def talkid(self, obj):
        return str(obj.talk_id)
    talkid.short_description = "Tk ID"
    list_display = ('id', 'url', 'title', 'talkid', 'talk')
    ordering = ('-id',)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('id', 'frab_id', 'name', 'abstract', 'description', 'doppelgaenger_of',)
    ordering = ('-id',)
    search_fields = ('id', 'frab_id', 'name',)


@admin.register(Type_of)
class TypeofAdmin(admin.ModelAdmin):
    list_display = ('id', 'type',)


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator',)


@admin.register(Tracks)
class TracksAdmin(admin.ModelAdmin):
    list_display = ('id', 'track',)


@admin.register(Rooms)
class RoomsAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'building', )


@admin.register(Statistics_Speaker)
class StatisticsSpeakersAdmin(admin.ModelAdmin):
    def speakerid(self, obj):
        return str(obj.speaker_id)
    speakerid.short_description = "Sp ID"

    def average_wpm_formated(self, obj):
        try:
            return format(obj.average_wpm, ".1f")
        except:
            return "-"
    average_wpm_formated.short_description = "avg wpm"

    def average_spm_formated(self, obj):
        try:
            return format(obj.average_spm, ".1f")
        except:
            return "-"
    average_spm_formated.short_description = "avg spm"

    list_display = ('id', 'speakerid', 'speaker', 'language', 'average_wpm_formated', 'average_spm_formated', 'words', 'strokes', 'time_delta', 'recalculate_statistics', 'n_most_frequent_words',)
    ordering = ('-id', )


@admin.register(Statistics_Event)
class StatisticsEventAdmin(admin.ModelAdmin):
    def average_wpm_formated(self, obj):
        try:
            return format(obj.average_wpm, ".1f")
        except:
            return "-"
    average_wpm_formated.short_description = "avg wpm"

    def average_spm_formated(self, obj):
        try:
            return format(obj.average_spm, ".1f")
        except:
            return "-"
    average_spm_formated.short_description = "avg spm"

    list_display = ('id', 'event', 'language', 'average_wpm_formated', 'average_spm_formated', 'words', 'strokes', 'time_delta', 'recalculate_statistics', 'n_most_frequent_words', )
    ordering = ('-id', )


#admin.site.register(Tracks)
#admin.site.register(Links)
#admin.site.register(Type_of)
#admin.site.register(Speaker)
#admin.site.register(Event_Days)
#admin.site.register(Rooms)
#admin.site.register(Language)
#admin.site.register(Statistics_Raw_Data)
#admin.site.register(Statistics_Speaker)
#admin.site.register(Statistics_Event)
#admin.site.register(Transcript)
#admin.site.register(Talk_Persons)
