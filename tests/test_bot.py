from unittest import TestCase

from mock import DEFAULT, MagicMock, patch

from ircpdb.bot import IrcpdbBot


class TestBot(TestCase):
    def setUp(self):
        self.arbitrary_channel = '#debugger_hangout'
        self.arbitrary_nickname = 'testAccount'
        self.arbitrary_server = 'irc.mycompany.org'
        self.arbitrary_port = 6667
        self.arbitrary_password = '1qaz2wsx'
        self.arbitrary_limit_access_to = []
        self.arbitrary_message_wait_seconds = 0.8
        self.arbitrary_paste_minimum_response_length = 1000
        self.arbitrary_activation_timeout = 60
        self.bot = IrcpdbBot(
            self.arbitrary_channel,
            self.arbitrary_nickname,
            self.arbitrary_server,
            self.arbitrary_port,
            self.arbitrary_password,
            self.arbitrary_limit_access_to,
            self.arbitrary_message_wait_seconds,
            self.arbitrary_paste_minimum_response_length,
            self.arbitrary_activation_timeout
        )

    def test_does_not_allow_command_execution_if_not_in_limit_access_to(self):
        not_allowed_nickname = 'mynickname'
        allowed_nicknames = []
        arbitrary_command = 'alpha'

        event = MagicMock()
        event.source.nick = not_allowed_nickname

        self.bot.limit_access_to = allowed_nicknames

        with patch.multiple(
            self.bot, send_user_message=DEFAULT, send_channel_message=DEFAULT
        ) as mocked:
            self.bot.do_command(event, arbitrary_command)

            if not mocked['send_user_message'].called:
                self.fail(
                    'User was not notified that he is not allowed to run '
                    'commands.'
                )
            if mocked['send_channel_message'].called:
                self.fail(
                    'Message was sent to the channel.'
                )
