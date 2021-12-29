from django import template
from django.utils.html import escape
from django.utils.safestring import SafeData, mark_safe
from django.template.defaultfilters import stringfilter

register = template.Library()


REPLACES = {
    r"&lt;b&gt;": "<b>",
    r"&lt;/b&gt;": "</b>",
    r"&lt;i&gt;": "<i>",
    r"&lt;/i&gt;": "</i>",
    r"&lt;u&gt;": "<u>",
    r"&lt;/u&gt;": "</u>",
    r"&lt;s&gt;": "<s>",
    r"&lt;/s&gt;": "</s>",
    }


@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def simple_style_tags(value, autoescape=True):
    """
    Unescapes simple style-tags <b>, <i>, <u>, <s>.
    """
    autoescape = autoescape and not isinstance(value, SafeData)
    if autoescape:
        value = escape(value)

    print(value)

    for needle, replacement in REPLACES.items():
        value = value.replace(needle, replacement)

    return mark_safe(value)
