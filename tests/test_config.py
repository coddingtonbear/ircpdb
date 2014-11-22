from unittest import TestCase

from mock import patch

from ircpdb.debugger import Ircpdb, DEFAULT_PARAMS


class TestConfig(TestCase):
    @patch('ircpdb.debugger.IrcpdbBot')
    @patch('os.fdopen')
    @patch('os.pipe', return_value=(None, None))
    @patch('pdb.Pdb.__init__')
    def test_uri_only(self, pdb_init, pipe, fdopen, bot):
        uri = 'irc://adam:pwd@ircserver.com:5000/#chan?limit_access_to=a,b'

        Ircpdb(uri)

        expected_params = {
            'server': 'ircserver.com',
            'nickname': 'adam',
            'password': 'pwd',
            'port': 5000,
            'channel': '#chan',
            'limit_access_to': ['a', 'b'],

            # Defaults
            'dpaste_minimum_response_length': (
                DEFAULT_PARAMS['dpaste_minimum_response_length']
            ),
            'message_wait_seconds': (
                DEFAULT_PARAMS['message_wait_seconds']
            )
        }
        bot.assert_called_with(**expected_params)

    @patch('ircpdb.debugger.IrcpdbBot')
    @patch('os.fdopen')
    @patch('os.pipe', return_value=(None, None))
    @patch('pdb.Pdb.__init__')
    def test_kwargs_override_uri(self, pdb_init, pipe, fdopen, bot):
        uri = 'irc://adam:pwd@ircserver.com:5000/#chan?limit_access_to=a,b'
        kwargs = {
            'nickname': 'theodore',
            'password': 'realpwd',
            'port': 8088,
            'channel': '#testroom',
            'limit_access_to': ['theodore']
        }

        Ircpdb(uri, **kwargs)

        expected_params = {
            'nickname': kwargs['nickname'],
            'password': kwargs['password'],
            'port': kwargs['port'],
            'channel': kwargs['channel'],
            'limit_access_to': kwargs['limit_access_to'],

            # From URI
            'server': 'ircserver.com',

            # Defaults
            'dpaste_minimum_response_length': (
                DEFAULT_PARAMS['dpaste_minimum_response_length']
            ),
            'message_wait_seconds': (
                DEFAULT_PARAMS['message_wait_seconds']
            )
        }
        bot.assert_called_with(**expected_params)
