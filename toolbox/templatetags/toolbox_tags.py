from __future__ import unicode_literals
from django.template.base import Library
from django.template.defaultfilters import stringfilter
register = Library()


@register.filter(is_safe=True)
@stringfilter
def dropcap(value):
    """
    Wraps the first character in a <span> tag with a .dropcap class
    that can be used to make it bigger than the surrounding text.
    """
    return value and "<span class='dropcap'>%s</span>%s" % (
        value[0].upper(),
        value[1:]
    )


@register.filter(is_safe=True)
@stringfilter
def emdashes(html):
    """
    Replace any '--' with '&mdash;'
    """
    return html.replace("--", "&mdash;")
