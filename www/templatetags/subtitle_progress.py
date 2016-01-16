from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ..views import _progress_bar, seconds

register = template.Library()

@register.filter(needs_autoescape=True)
def progress_bar(subtitle, small_translations=False, autoescape=None):
    if subtitle.is_original_lang:
        temp = 'www/progress_bar_original.html'
        bar = _progress_bar(total=seconds(subtitle.talk.video_duration),
                            green=seconds(subtitle.time_quality_check_done),
                            orange=seconds(subtitle.time_processed_syncing),
                            red=seconds(subtitle.time_processed_transcribing))
    else:
        temp = 'www/progress_bar_translation.html'
        bar = _progress_bar(total=seconds(subtitle.talk.video_duration),
                            green=seconds(subtitle.time_processed_translating))
        if small_translations:
            bar['small'] = True

    return mark_safe(render_to_string(temp, {'value': bar}))
