from six import text_type


def comma_separated_list(string):
    if not string:
        return []
    return [
        text_type(v) for v in string.split(',')
    ]
