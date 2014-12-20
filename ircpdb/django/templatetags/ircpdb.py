from __future__ import absolute_import

from django import template

import ircpdb


register = template.Library()


@register.simple_tag(name='set_trace', takes_context=True)
def ircpdb_trace(context, *args, **kwargs):
    ircpdb.set_trace(*args, **kwargs)
