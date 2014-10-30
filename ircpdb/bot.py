from multiprocessing import Queue
import random

from irc import strings
from irc.bot import SingleServerIRCBot, ServerSpec


class IrcpdbBot(SingleServerIRCBot):
    def __init__(
        self, channel, nickname, server, port, password,
        **connect_params
    ):
        self.channel = channel
        self.queue = Queue()
        server = ServerSpec(server, port, password)
        super(IrcpdbBot, self).__init__(
            [server], nickname, nickname, **connect_params
        )

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "-" + random.randrange(0, 9999))

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if (
            len(a) > 1
            and strings.lower(a[0]) == strings.lower(
                self.connection.get_nickname()
            )
        ):
            self.do_command(e, a[1].strip())
        return

    def do_command(self, e, cmd):
        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        else:
            self.queue.put(cmd.strip())

    def process_forever(self, inhandle, outhandle, timeout=0.1):
        self._connect()
        while True:
            messages = inhandle.read()
            if messages.strip():
                for message in messages.split('\n'):
                    print ">> %s" % message.strip()
                    self.connection.send_raw(
                        'PRIVMSG %s :%s' % (
                            self.channel,
                            message.strip()
                        )
                    )

            self.manifold.process_once(timeout)

            while True:
                if self.queue.empty():
                    break
                message = self.queue.get(block=False)
                print "<< %s" % message.strip()
                outhandle.write(u'%s\n' % message)
