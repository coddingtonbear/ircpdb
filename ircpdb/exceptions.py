
class IrcpdbError(Exception):
    pass


class NoChannelSelected(IrcpdbError, ValueError):
    pass
