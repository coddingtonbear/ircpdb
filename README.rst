ircpdb - Remotely and collaboratively debug your Python application via IRC
===========================================================================

Ircpdb is an adaptation of rpdb that, instead of opening a port and
allowing you to debug over telnet, connects to a configurable IRC
channel so you can collaboratively debug an application remotely.

.. code-block::

    import ircpdb
    ircpdb.set_trace(
        channel="#debugger_hangout",
    )  # Warning!  This is dangerous -- see `Security Disclaimer` below.

By default, ircpdb will create the channel you specify on Freenode
and randomly select a nickname for itself, but you can feel free to
configure ircpdb to connect anywhere:

.. code-block::

    import ircpdb
    ircpdb.set_trace(
        channel="#debugger_hangout",
        nickname='im_a_debugger',
        server='irc.mycompany.org',
        limit_access_to=['mynickname'],  # See 'Security Disclaimer' below.
        port=6667,
        ssl=True,
    )  # See 'Options' below for descriptions of the above arguments

Upon reaching ``set_trace()``, your script will "hang" and the only way to get
it to continue is to access ircpdb by talking to the user that connected to the
above IRC channel.

By default, the debugger will enter the channel you've specified using a
username starting with the hostname of the computer from which it was
launched (in the following example: 'MyHostname').  To interact with
the debugger, just send messages in the channel prefixed with "MyHostname:",
or simply "!".

For example, the following two commands are equivalent, and each will
display the pdb help screen (be sure to replace 'MyHostname' with whatever
username the bot selected)::

    !help

::

    MyHostname: help

Installation
------------

From ``pip``::

    pip install ircpdb

Options
-------

* ``channel`` (**REQUIRED**): The name of the channel (starting with ``#``)
  to connect to on the IRC server.
* ``nickname``: The nickname to use when connecting. Note that an alternate
  name will be selected if this name is already in use. Defaults to using
  the hostname of the machine on which the debugger was executed.
* ``server``: The hostname or IP address of the IRC server.
  Default: ``chat.freenode.net``.
* ``port``: The port number of the IRC server.  Default: ``6697``.
* ``ssl``: Use SSL when connecting to the IRC server?  Default: ``True``.
* ``password``: The server password (if necessary) for the IRC server.
  Default: ``None``.
* ``limit_access_to``: A list of nicknames that are allowed to interact
  with the debugger.  An empty list allows all nicknames to access the
  debugger.  Default: ``[]``.
* ``message_wait_seconds``: The number of seconds that the bot should
  wait between sending messages on IRC.  Many servers, including Freenode,
  will kick clients that send too many messages in too short of a time
  frame.  Default: ``0.8`` seconds.
* ``dpaste_minimum_response_length``: Try to post messages this length
  or longer to `dpaste <http://dpaste.com/>`_ rather than sending
  each line individually via IRC.  This is a useful parameter to use
  if you happen to be connected to a server having very austere
  limits on the number of lines a client can send per minute.
  Default: ``10`` lines.

Security Disclaimer
-------------------

The way that this library works is **inherently** **dangerous**; given that
you're able to execute arbitrary Python code from within your debugger,
it is strongly recommended that you take all reasonable measures to ensure
that you control who are able to execute debugger commands.

To mitigate these dangers, you should always use an SSL-capable IRC
server (read: leave the ``ssl`` argument set to it's default: ``True``)
and use *at* *least* one of the following options:

* Use ``limit_access_to`` to limit which users (by nickname) are allowed to
  interact with the debugger.  Note that this does not mitigate your
  risk completely due to the way nicknames are handled on IRC servers.
* *and/or*, and this is considerably safer, connect to an IRC server
  you or a company you work for owns rather than Freenode (the default).

Just to make absolutely sure this is clear: you're both responsible for
determining what level of risk you are comfortable with, and for taking
appropriate actions to mitigate that risk.

As is clearly and thunderously stated library's license (see the included
``LICENSE.txt``)::

    THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
    ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
    OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
    OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
    SUCH DAMAGE.

Good luck, and happy debugging!

Troubleshooting
---------------

If you do not see the bot entering your specified channel, try increasing
the logging level by adding the following lines above your trace to gather
a little more information about problems that may have occurred while 
connecting to the IRC server:

.. code-block::

   import logging
   logging.basicConfig(level=logging.DEBUG)

Author(s)
---------
Adam Coddington <me@adamcoddington.net> - http://adamcoddington.net/

This library is a fork of rpdb, and the underpinnings of this library
are owed to Bertrand Janin <b@janin.com> - http://tamentis.com/ and
all other contributors to `rpdb <https://github.com/tamentis/rpdb>`
including the following:

 - Ken Manheimer - @kenmanheimer
 - Steven Willis - @onlynone
 - Jorge Niedbalski R <niedbalski@gmail.com>
 - Cyprien Le Pannérer <clepannerer@edd.fr>
 - k4ml <kamal.mustafa@gmail.com>
 - Sean M. Collins <sean@coreitpro.com>
