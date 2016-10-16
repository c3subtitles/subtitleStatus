from django import template
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from simplejson import dumps

register = template.Library()

@register.filter(needs_autoescape=True)
def word_cloud(word_frequencies, element_id, autoescape=True):
    words = []
    escape = conditional_escape if autoescape else lambda x: x
    for word, frequency in word_frequencies.items():
        words.append({'text': escape(word), 'weight': frequency})

    wordlist = dumps(words, ensure_ascii=False)
    return mark_safe(render_to_string('www/word_cloud.html',
                                      {'words': wordlist,
                                       'element_id': element_id}))
