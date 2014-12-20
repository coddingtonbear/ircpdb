from __future__ import absolute_import

from django import template

import ircpdb
from ircpdb.parse import PARAMS


register = template.Library()


@register.simple_tag(name='set_trace', takes_context=True)
def ircpdb_trace(context, *args, **kwargs):
    # Convert incoming data into the appropriate format
    for name, converter in PARAMS.items():
        if name in kwargs:
            kwargs[name] = converter(kwargs[name])

    ircpdb.set_trace(*args, **kwargs)
    return ''
