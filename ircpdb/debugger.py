import logging
import os
import pdb
import socket
import ssl as ssllib
import sys
from threading import Thread
import traceback

from irc.connection import Factory
import six

from . import paste_backends
from .bot import IrcpdbBot
from .exceptions import NoAllowedNicknamesSelected, NoChannelSelected
from .parse import parse_irc_uri


logger = logging.getLogger(__name__)


DEFAULT_PARAMS = {
    'channel': None,
    'nickname': None,
    'server': 'chat.freenode.net',
    'port': 6697,
    'password': None,
    'ssl': True,
    'limit_access_to': None,
    'message_wait_seconds': 0.8,
    'paste_minimum_response_length': 20,
    'activation_timeout': 60
}


class Ircpdb(pdb.Pdb):
    def __init__(self, uri=None, **kwargs):
        """Initialize the socket and initialize pdb."""
        params = DEFAULT_PARAMS.copy()
        params.update(parse_irc_uri(uri))
        params.update(kwargs)

        # Backup stdin and stdout before replacing them by the socket handle
        self.old_stdout = sys.stdout
        self.old_stdin = sys.stdin
        self.read_timeout = 0.1

        if not params.get('limit_access_to'):
            raise NoAllowedNicknamesSelected(
                "You must specify a list of nicknames that are allowed "
                "to interact with the debugger using the "
                "`limit_access_to` keyword argument."
            )
        elif isinstance(params.get('limit_access_to'), six.string_types):
            params['limit_access_to'] = [params.get('limit_access_to')]

        connect_params = {}
        if not params.get('nickname'):
            params['nickname'] = socket.gethostname().split('.')[0]
        if not params.get('channel'):
            raise NoChannelSelected(
                "You must specify a channel to connect to using the "
                "`channel` keyword argument."
            )
        if params.get('ssl'):
            connect_params['connect_factory'] = (
                Factory(wrapper=ssllib.wrap_socket)
            )

        # Writes to stdout are forbidden in mod_wsgi environments
        try:
            logger.info(
                "ircpdb has connected to %s:%s on %s\n",
                params.get('server'),
                params.get('port'),
                params.get('channel')
            )
        except IOError:
            pass

        r_pipe, w_pipe = os.pipe()
        # The A pipe is from the bot to pdb
        self.p_A_pipe = os.fdopen(r_pipe, 'r')
        self.b_A_pipe = os.fdopen(w_pipe, 'w')

        r_pipe, w_pipe = os.pipe()
        # The B pipe is from pdb to the bot
        self.b_B_pipe = os.fdopen(r_pipe, 'r')
        self.p_B_pipe = os.fdopen(w_pipe, 'w')

        pdb.Pdb.__init__(
            self,
            stdin=self.p_A_pipe,
            stdout=self.p_B_pipe,
        )

        paste_backend = paste_backends.GistBackend()
        self.bot = IrcpdbBot(
            channel=params.get('channel'),
            nickname=params.get('nickname'),
            server=params.get('server'),
            port=params.get('port'),
            password=params.get('password'),
            limit_access_to=params.get('limit_access_to'),
            message_wait_seconds=params.get('message_wait_seconds'),
            paste_minimum_response_length=(
                params.get('paste_minimum_response_length')
            ),
            paste_backend=paste_backend,
            activation_timeout=params.get('activation_timeout'),
            **connect_params
        )

    def shutdown(self):
        """Revert stdin and stdout, close the socket."""
        sys.stdout = self.old_stdout
        sys.stdin = self.old_stdin
        pipes = [
            self.p_A_pipe,
            self.p_B_pipe,
            self.b_A_pipe,
            self.b_B_pipe
        ]
        for pipe in pipes:
            try:
                pipe.close()
            except IOError:
                logger.warning(
                    "IOError encountered while closing a pipe; messages "
                    "may have been lost."
                )
        self.bot.disconnect()

    def do_continue(self, arg):
        """Clean-up and do underlying continue."""
        try:
            return pdb.Pdb.do_continue(self, arg)
        finally:
            self.shutdown()

    do_c = do_cont = do_continue

    def do_quit(self, arg):
        """Clean-up and do underlying quit."""
        try:
            return pdb.Pdb.do_quit(self, arg)
        finally:
            self.shutdown()

    do_q = do_exit = do_quit


def set_trace(*args, **kwargs):
    """Wrapper function to keep the same import x; x.set_trace() interface.

    We catch all the possible exceptions from pdb and cleanup.

    """
    if not args and 'DEFAULT_IRCPDB_URI' in os.environ:
        args = (
            os.environ['DEFAULT_IRCPDB_URI'],
        )
    debugger = Ircpdb(*args, **kwargs)
    try:
        irc_feeder = Thread(
            target=debugger.bot.process_forever,
            args=(debugger.b_B_pipe, debugger.b_A_pipe, ),
        )
        irc_feeder.daemon = True
        irc_feeder.start()

        debugger.set_trace(sys._getframe().f_back)
    except Exception:
        debugger.shutdown()
        traceback.print_exc()
