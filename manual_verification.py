import logging

import ircpdb

logging.basicConfig(level=logging.DEBUG)


def test():
    ircpdb.set_trace(
        limit_access_to='coddingtonbear'
    )


if __name__ == '__main__':
    test()
