from irc import strings
from irc.bot import SingleServerIRCBot, ServerSpec


class IrcpdbBot(SingleServerIRCBot):
    def __init__(
        self, channel, nickname, server, port, password, handle,
        **connect_params
    ):
        self.channel = channel
        self.handle = handle
        server = ServerSpec(server, port, password)
        super(IrcpdbBot, self).__init__(
            [server], nickname, nickname, **connect_params
        )

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

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
        self.connection.send_raw(
            'PRIVMSG %s :%s' % (
                e.source.nick,
                self.channel
            )
        )

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        else:
            self.handle.write(cmd)
            self.handle.write('\n')
        import time
        time.sleep(5)
        self.handle.write('Test\n')
        lines = self.handle.read()
        for line in lines.split('\n'):
            self.connection.send_raw(
                'PRIVMSG %s :%s' % (
                    self.channel,
                    line.strip()
                )
            )
