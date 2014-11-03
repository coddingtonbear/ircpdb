from unittest import TestCase

from mock import DEFAULT, MagicMock, patch

from ircpdb.debugger import Ircpdb


class TestDebugger(TestCase):
    def setUp(self):
        self.arbitrary_channel = '#debugger_hangout'
        self.arbitrary_allowed_nickname = 'alpha'
        self.arbitrary_limit_access_to = [
            self.arbitrary_allowed_nickname
        ]
        self.debugger = Ircpdb(
            channel=self.arbitrary_channel,
            limit_access_to=self.arbitrary_limit_access_to
        )

    def test_pipes_are_closed_and_disconnecting(self):
        with patch.object(self.debugger.bot, 'disconnect') as disconnect:
            self.debugger.shutdown()

            if not disconnect.called:
                self.fail("Bot was not ordered to disconnect.")

        for pipe_name in [
            'p_A_pipe',
            'p_B_pipe',
            'b_A_pipe',
            'b_B_pipe',
        ]:
            if not getattr(self.debugger, pipe_name).closed:
                self.fail(
                    "Pipe '%s' is not closed." % pipe_name
                )
