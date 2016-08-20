import abc
import json

import requests


class PasteBackend(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def paste(self, output):
        """Paste output to your pastebin of choice.

        :type output: list of basestring
        :param output: The output lines we'd like sent to the pastebin.
        :rtype: string
        :returns: URL to return to the shell.
        """
        return


class GistBackend(PasteBackend):
    def paste(self, lines):
        response = requests.post(
            'https://api.github.com/gists',
            data=json.dumps(
                {
                    'files': {
                        'output.txt': {
                            'content': '\n'.join(lines)
                        }
                    }
                }
            )
        )
        return response.json()['html_url']
