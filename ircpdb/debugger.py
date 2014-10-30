import pdb
import socket
import ssl as ssllib
import sys
from threading import Thread
import time
import traceback

from irc.connection import Factory
from six import StringIO

from .exceptions import NoChannelSelected
from .bot import IrcpdbBot


class Ircpdb(pdb.Pdb):
    def __init__(
        self, channel=None, nickname=None,
        server='chat.freenode.net', port=6667,
        password=None, ssl=True
    ):
        """Initialize the socket and initialize pdb."""

        # Backup stdin and stdout before replacing them by the socket handle
        self.old_stdout = sys.stdout
        self.old_stdin = sys.stdin
        self.read_timeout = 0.1

        connect_params = {}
        if not nickname:
            nickname = socket.gethostname().split('.')[0]
        if not channel:
            raise NoChannelSelected(
                "You must specify a channel to connect to."
            )
        if ssl:
            connect_params['connect_factory'] = (
                Factory(wrapper=ssllib.wrap_socket)
            )

        # Writes to stdout are forbidden in mod_wsgi environments
        try:
            sys.stderr.write(
                "ircpdb has connected to %s:%s on %s\n" % (
                    server,
                    port,
                    channel
                )
            )
        except IOError:
            pass

        self.inhandle = StringIO()
        self.outhandle = StringIO()
        pdb.Pdb.__init__(
            self, completekey='tab', stdin=self.inhandle, stdout=self.outhandle
        )
        #sys.stdout = sys.stdin = self.handle

        self.bot = IrcpdbBot(
            channel=channel,
            nickname=nickname,
            server=server,
            port=port,
            password=password,
            **connect_params
        )

    def start_bot(self):
        self.bot.start()

    def shutdown(self):
        """Revert stdin and stdout, close the socket."""
        sys.stdout = self.old_stdout
        sys.stdin = self.old_stdin
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

    def do_EOF(self, arg):
        """Clean-up and do underlying EOF."""
        pass


def set_trace(**kwargs):
    """Wrapper function to keep the same import x; x.set_trace() interface.

    We catch all the possible exceptions from pdb and cleanup.

    """
    debugger = Ircpdb(**kwargs)
    try:
        irc_feeder = Thread(
            target=debugger.bot.process_forever,
            args=(debugger.outhandle, debugger.inhandle, ),
        )
        irc_feeder.daemon = True
        irc_feeder.start()

        debugger.set_trace(sys._getframe().f_back)
    except Exception:
        debugger.shutdown()
        traceback.print_exc()
