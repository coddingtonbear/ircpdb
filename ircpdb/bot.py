import fcntl
import logging
from multiprocessing import Queue
import os
import random
import time

from irc import strings
from irc.bot import SingleServerIRCBot, ServerSpec


logger = logging.getLogger(__name__)


class IrcpdbBot(SingleServerIRCBot):
    def __init__(
        self, channel, nickname, server, port, password,
        limit_access_to, message_wait_seconds,
        **connect_params
    ):
        self.channel = channel
        self.queue = Queue()
        self.joined = False
        self.pre_join_queue = []
        self.message_wait_seconds = message_wait_seconds
        self.limit_access_to = limit_access_to
        server = ServerSpec(server, port, password)
        super(IrcpdbBot, self).__init__(
            [server], nickname, nickname, **connect_params
        )

    def on_nicknameinuse(self, c, e):
        c.nick(
            u"%s-%s" % (
                c.get_nickname(),
                random.randrange(0, 9999)
            )
        )

    def on_welcome(self, c, e):
        logger.debug('Received welcome message, joining %s', self.channel)
        c.join(self.channel)
        self.joined = True
        for username, message in self.pre_join_queue:
            self.send_user_message(username, message)

    def on_privmsg(self, c, e):
        self.send_user_message(
            e.source.nick,
            "Ircdb currently supports sending/receiving messages "
            "using only the IRC channel."
        )

    def on_pubmsg(self, c, e):
        # Check if this message is prefixed with the bot's username:
        a = e.arguments[0].split(":", 1)
        if (
            len(a) > 1
            and strings.lower(a[0]) == strings.lower(
                self.connection.get_nickname()
            )
        ):
            self.do_command(e, a[1].strip())

        # And, check if the argument was prefixed with a '!'.
        if e.arguments[0][0] == '!':
            self.do_command(e, e.arguments[0][1:].strip())
        return

    def do_command(self, e, cmd):
        logger.debug('Received command: %s', cmd)
        nickname = e.source.nick
        if self.limit_access_to and nickname not in self.limit_access_to:
            self.send_channel_message(
                "I'm sorry, %s, you are not allowed to give commands "
                "to this debugger.  Please ask one of the following "
                "users for permission to use the debugger: %s." % (
                    nickname,
                    ', '.join(self.limit_access_to)
                )
            )
            return

        if cmd.startswith("!allow"):
            allows = cmd.split(' ')
            self.limit_access_to.extend(allows[1:])
            self.send_channel_message(
                "The following users have been granted access to the debugger:"
                " %s." % (
                    ', '.join(allows[1:])
                )
            )
        else:
            self.queue.put(cmd.strip())

    def send_channel_message(self, message):
        return self.send_user_message(
            self.channel,
            message,
        )

    def send_user_message(self, username, message):
        message_stripped = message.strip()
        if not self.joined:
            logger.warning(
                'Tried to send message %s, '
                'but was not yet joined to channel. Queueing...',
                message
            )
            self.pre_join_queue.append(
                (username, message, )
            )
            return
        if message_stripped:
            chunk_size = 450
            if len(message_stripped) > chunk_size:
                message_parts = [
                    message_stripped[i:i+chunk_size]
                    for i in range(0, len(message_stripped), chunk_size)
                ]
            else:
                message_parts = [message_stripped]
            for part in message_parts:
                self.connection.send_raw(
                    'PRIVMSG %s :%s' % (
                        username,
                        part
                    )
                )
                if self.message_wait_seconds:
                    time.sleep(self.message_wait_seconds)

    def process_forever(self, inhandle, outhandle, timeout=0.1):
        self._connect()
        # Let's mark out inhandle as non-blocking
        fcntl.fcntl(inhandle, fcntl.F_SETFL, os.O_NONBLOCK)
        while True:
            try:
                messages = inhandle.read()
            except IOError:
                messages = None
            if messages:
                for message in messages.split('\n'):
                    logger.debug('>> %s', message)
                    self.send_channel_message(message.strip())

            try:
                self.manifold.process_once(timeout)
            except UnicodeDecodeError:
                # This just *happens* -- I think these are coming from
                # maybe MOTD messages?  It isn't clear.
                logger.warning(
                    'UnicodeDecodeError raised while processing messages.'
                )

            while True:
                if self.queue.empty():
                    break
                message = self.queue.get(block=False)
                logger.debug('<< %s', message)
                outhandle.write(u'%s\n' % message)
                outhandle.flush()
