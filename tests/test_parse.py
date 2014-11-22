from unittest import TestCase

from ircpdb.parse import parse_irc_uri


class TestURIParser(TestCase):
    def test_parser(self):
        uri = (
            'irc+ssl://nickname:password@hostname:100/#channel?'
            'message_wait_seconds=0.5&'
            'limit_access_to=alpha,beta,delta'
        )

        actual_result = parse_irc_uri(uri)
        expected_result = {
            'server': 'hostname',
            'ssl': True,
            'nickname': 'nickname',
            'password': 'password',
            'port': 100,
            'channel': '#channel',
            'message_wait_seconds': 0.5,
            'limit_access_to': ['alpha', 'beta', 'delta']
        }

        self.assertEqual(
            expected_result,
            actual_result,
        )

    def test_parser_minimal(self):
        uri = (
            'irc://hostname/#channel?'
        )

        actual_result = parse_irc_uri(uri)
        expected_result = {
            'server': 'hostname',
            'channel': '#channel',
            'ssl': False,
        }

        self.assertEqual(
            expected_result,
            actual_result,
        )
