
class IrcpdbError(Exception):
    pass


class NoChannelSelected(IrcpdbError, ValueError):
    pass


class NoAllowedNicknamesSelected(IrcpdbError, ValueError):
    pass


class DpasteError(IrcpdbError, IOError):
    pass
