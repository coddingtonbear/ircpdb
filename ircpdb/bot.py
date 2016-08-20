import fcntl
import logging
from multiprocessing import Queue
import os
import random
import socket
import textwrap
import time

from irc import strings
from irc.bot import SingleServerIRCBot, ServerSpec
import six

from .exceptions import PasteError


logger = logging.getLogger(__name__)


class IrcpdbBot(SingleServerIRCBot):
    PROMPT = 'ready'

    def __init__(
        self, channel, nickname, server, port, password,
        limit_access_to, message_wait_seconds,
        paste_minimum_response_length,
        activation_timeout,
        paste_backend=None,
        **connect_params
    ):
        self.channel = channel
        self.queue = Queue()
        self.joined = False
        self.activated = False
        self.pre_join_queue = []
        self.message_wait_seconds = message_wait_seconds
        self.paste_minimum_response_length = paste_minimum_response_length
        self.paste_backend = paste_backend
        self.activation_timeout = activation_timeout
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

        self.send_channel_message(
            [
                "Debugger ready (on host %s)" % socket.gethostname(),
                (
                    "The following users are able to interact with this "
                    "debugger: %s" % (
                        ', '.join(self.limit_access_to)
                    )
                ),
                (
                    "Please prefix debugger commands with either '!' or "
                    "'%s:'. For pdb help, say '!help'; for a list of "
                    "ircpdb-specific commands, say '!!help'." % (
                        self.connection.nickname
                    )
                )
            ],
            paste=False
        )
        for username, message in self.pre_join_queue:
            self.send_user_message(username, message)
        self.send_prompt()

    def on_privmsg(self, c, e):
        self.send_user_message(
            e.source.nick,
            "I'm sorry, %s, %s only accepts commands from the %s "
            "IRC channel." % (
                e.source.nick,
                self.connection.nickname,
                self.channel,
            )
        )

    def on_pubmsg(self, c, e):
        # Check if this message is prefixed with the bot's username:
        a = e.arguments[0].split(":", 1)
        if (
            len(a) > 1 and
            strings.lower(a[0]) == strings.lower(
                self.connection.get_nickname()
            )
        ):
            self.do_command(e, a[1].strip())

        # And, check if the argument was prefixed with a '!'.
        if e.arguments[0][0] == '!':
            self.do_command(e, e.arguments[0][1:].strip())
        return

    def do_command(self, e, cmd):
        self.activated = True
        logger.debug('Received command: %s', cmd)
        nickname = e.source.nick
        if nickname not in self.limit_access_to:
            self.send_user_message(
                nickname,
                "I'm sorry, %s, you are not allowed to give commands "
                "to this debugger." % (
                    nickname,
                )
            )
            return

        if cmd.startswith("!allow"):
            allows = cmd.split(' ')
            usernames = allows[1:]
            if not self.limit_access_to:
                self.limit_access_to.append(nickname)
            self.limit_access_to.extend(usernames)
            self.send_channel_message(
                "The following users have been granted access to the debugger:"
                " %s." % (
                    ', '.join(usernames)
                )
            )
        elif cmd.startswith("!forbid"):
            forbids = cmd.split(' ')
            usernames = forbids[1:]
            try:
                for username in usernames:
                    self.limit_access_to.remove(username)
                self.send_channel_message(
                    "The following users have been forbidden access to the "
                    "debugger: %s." % (
                        ', '.join(usernames)
                    )
                )
            except ValueError:
                self.send_channel_message(
                    "The users %s are not in the 'allows' list.  You must "
                    "have a defined 'allows' list to remove users from it." % (
                        ', '.join(usernames)
                    )
                )
            if not self.limit_access_to:
                self.send_channel_message(
                    "No users are allowed to interact with the debugger; "
                    "continuing from breakpoint."
                )
                self.queue.put('continue')

        elif cmd.startswith("!set_paste_minimum_response_length"):
            value = cmd.split(' ')
            try:
                self.paste_minimum_response_length = int(value[1])
                self.send_channel_message(
                    "Messages longer than %s lines will now be posted "
                    "to paste if possible." % (
                        self.paste_minimum_response_length
                    )
                )
            except (TypeError, IndexError, ValueError):
                self.send_channel_message(
                    "An error was encountered while setting the "
                    "paste_minimum_response_length setting. %s"
                )
        elif cmd.startswith("!set_message_wait_seconds"):
            value = cmd.split(' ')
            try:
                self.message_wait_seconds = float(value[1])
                self.send_channel_message(
                    "There will be a delay of %s seconds between "
                    "sending each message." % (
                        self.message_wait_seconds
                    )
                )
            except (TypeError, IndexError, ValueError):
                self.send_channel_message(
                    "An error was encountered while setting the "
                    "message_wait_seconds setting."
                )
        elif cmd.startswith("!help"):
            available_commands = textwrap.dedent("""
                Available Commands:
                * !!allow NICKNAME
                  Add NICKNAME to the list of users that are allowed to
                  interact with the debugger. Current value: {limit_access_to}.

                * !!forbid NICKNAME
                  Remove NICKNAME from the list of users that are allowed
                  to interact with the debugger.

                * !!set_paste_minimum_response_length INTEGER
                  Try to send messages this length or longer in lines
                  to paste rather than sending them to IRC directly.
                  Current value: {paste_minimum_response_length}.

                * !!set_message_wait_seconds FLOAT
                  Set the number of seconds to wait between sending messages
                  (this is a measure used to prevent being kicked from
                  Freenode and other IRC servers that enforce limits on the
                  number of messages a client an send in a given period of
                  time. Current value: {message_wait_seconds}.
            """.format(
                limit_access_to=self.limit_access_to,
                paste_minimum_response_length=(
                    self.paste_minimum_response_length
                ),
                message_wait_seconds=self.message_wait_seconds,
            ))
            self.send_channel_message(
                available_commands,
                paste=True,
            )
        else:
            self.queue.put(cmd.strip())

    def send_channel_message(self, message, paste=None):
        return self.send_user_message(
            self.channel,
            message,
            paste=paste,
        )

    def send_user_message(self, username, message, paste=None):
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

        if isinstance(message, six.string_types):
            message_stripped = message.strip()
            lines = message_stripped.split('\n')
        else:
            lines = message
        chunked = self.get_chunked_lines(lines)
        try:
            long_response = len(chunked) >= self.paste_minimum_response_length
            if (long_response and paste is None) or paste is True:
                paste_url = self.send_lines_to_paste(lines)
                self.send_lines(
                    username, "See %s (%s lines in result)" % (
                        paste_url,
                        len(lines)
                    )
                )
                return
        except PasteError:
            pass
        self.send_lines(username, chunked)

    def send_prompt(self):
        if not self.joined:
            # We'll display a 'ready' message once we've joined anyway;
            # let's just silently drop this.
            return
        self.send_lines(
            self.channel,
            self.PROMPT,
            command='ACTION',
        )

    def get_chunked_lines(self, lines, chunk_size=400):
        chunked_lines = []
        for line in lines:
            if len(line) > chunk_size:
                chunked_lines.extend([
                    line[i:i+chunk_size]
                    for i in range(0, len(line), chunk_size)
                ])
            else:
                chunked_lines.append(line)
        return chunked_lines

    def send_lines_to_paste(self, lines):
        try:
            return self.paste_backend.paste(lines)
        except Exception as e:
            raise PasteError(str(e))

    def send_lines(self, target, lines, command=None):
        prefix = ':'
        suffix = ''
        if command is not None:
            prefix = ':\001%s ' % command
            suffix = '\001'
        if isinstance(lines, six.string_types):
            lines = [lines]
        for part in lines:
            if not part:
                continue
            self.connection.send_raw(
                'PRIVMSG %s %s%s%s' % (
                    target,
                    prefix,
                    part,
                    suffix
                )
            )
            if self.message_wait_seconds:
                time.sleep(self.message_wait_seconds)

    def process_forever(self, inhandle, outhandle, timeout=0.1):
        self._connect()
        # Let's mark out inhandle as non-blocking
        fcntl.fcntl(inhandle, fcntl.F_SETFL, os.O_NONBLOCK)
        # Used for keeping track of when the bot was started
        # so we can disconnect for inactivity.
        started = time.time()
        # Keeps track of whether or not we're in the process of
        # disconnecting (queued the 'q' command)
        disconnecting = False

        while True:
            try:
                messages = inhandle.read()
            except IOError:
                messages = None
            if messages:
                for message in messages.split('(Pdb)'):
                    stripped = message.strip()
                    if stripped:
                        logger.debug('>> %s', stripped)
                        self.send_channel_message(stripped)
                self.send_prompt()

            try:
                self.reactor.process_once(timeout)
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

            if (
                time.time() > started + self.activation_timeout and
                not self.activated and
                not disconnecting
            ):
                self.send_channel_message(
                    [
                        "No response received within %s seconds; "
                        "disconnecting due to inactivity." % (
                            self.activation_timeout
                        )
                    ],
                    paste=False,
                )
                disconnecting = True
                self.queue.put('c')
