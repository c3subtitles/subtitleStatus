from django import template
from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from simplejson import dumps
from random import randint

register = template.Library()

@register.filter(needs_autoescape=True)
def word_cloud(word_frequencies, element_id, autoescape=True):
    """Generate a word cloud according to the frequency table
    `word_frequencies` and using the HTML ID `element_id`.

    If `word_frequencies` is empty, no content will be generated."""
    if not word_frequencies:
        return mark_safe('')

    words = []
    escape = conditional_escape if autoescape else lambda x: x
    for word, frequency in word_frequencies.items():
        words.append({'text': escape(word), 'weight': frequency})

    wordlist = dumps(words, ensure_ascii=False)
    return mark_safe(render_to_string('www/word_cloud.html',
                                      {'words': wordlist,
                                       'element_id': element_id}))


@register.inclusion_tag('www/scaled_word_cloud.html')
def common_words_cloud(item, height='23em', property='n_common_words', id=None):
    """Generate a word cloud from any object having a `n_common_words`
    property. A suitable HTML ID is generated from `item.id` if
    applicable, otherwise an id is generated randomly.

    The optional argument `height` will be used to scale the containing
    `div` element.

    Optionally, an alternative property may be specified using the
    `property` argument.

    The `id` argument allows to specify a suffix used for
    disambiguation of generated HTML IDs, for example to genarate
    multiple clouds for the same `item`."""

    context = {'words': getattr(item, property),
               'height': height,
               'id': getattr(item, 'id', randint(0, 16384)),
              }

    if id is not None:
        context['id'] = '%s-%s' % (context['id'], id)

    return context
