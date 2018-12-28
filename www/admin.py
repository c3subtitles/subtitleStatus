from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import admin
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


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('id', 'frab_id_talk', 'title',
                    'event', 'day', 'start',)
    list_filter = ('event', DayIndexFilter,)
    search_fields = ('title', 'event__acronym', 'frab_id_talk',)
    ordering = ('-event', 'date',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    date_hierarchy = 'start'
    list_display = ('acronym', 'title', 'start', 'days', 'city', 'building',)
    list_filter = ('city',)


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
            return '{} {}'.format(obj.state, stamp)
        else:
            return obj.state


    def pad_from_trint(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        first = selected[0]
        rest = ','.join(selected[1:])
        return HttpResponseRedirect(
            reverse('padFromTrint', args=[first, rest]))


    actions = ['pad_from_trint']
    list_display = ('id', 'talk', 'language', 'is_original_lang',
                    'status', 'complete', 'blacklisted',)
    list_filter = (LanguageFilter, 'is_original_lang', 'state', 'complete',
                   'blacklisted', )
    raw_id_fields = ('talk',)
    search_fields = ('talk__event__acronym', 'talk__title', 'talk__frab_id_talk',)


admin.site.register(Tracks)
admin.site.register(Links)
admin.site.register(Type_of)
admin.site.register(Speaker)
admin.site.register(States)
admin.site.register(Event_Days)
admin.site.register(Rooms)
admin.site.register(Language)
admin.site.register(Statistics_Raw_Data)
