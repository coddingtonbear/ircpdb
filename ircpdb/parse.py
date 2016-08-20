import sys

from six import text_type
from six.moves.urllib.parse import (
    parse_qs,
    urlparse,
    unquote
)

from .utils import comma_separated_list


PARAMS = {
    'message_wait_seconds': float,
    'paste_minimum_response_length': int,
    'limit_access_to': comma_separated_list,
    'activation_timeout': float,
}


def parse_irc_uri(uri):
    if not uri:
        return {}
    uri = uri.replace('#', '%23')

    parsed = urlparse(uri)
    if sys.version_info < (2, 7) and '?' in parsed.path:
        query = parsed.path[parsed.path.find('?')+1:]
        path = parsed.path[:parsed.path.find('?')]
    else:
        query = parsed.query
        path = parsed.path

    result = {}

    if parsed.hostname:
        result['server'] = parsed.hostname
    if parsed.scheme:
        result['ssl'] = '+ssl' in parsed.scheme
    if path and len(path) > 1:
        result['channel'] = unquote(path[1:])
    if parsed.username:
        result['nickname'] = unquote(parsed.username)
    if parsed.password:
        result['password'] = unquote(parsed.password)
    if parsed.port:
        result['port'] = int(parsed.port)

    if query:
        for keyword, value_list in parse_qs(query).items():
            value = value_list[0]
            result[keyword] = PARAMS.get(keyword, text_type)(value)

    return result
