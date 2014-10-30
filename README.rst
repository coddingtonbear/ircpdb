ircpdb - Remotely debug your Python application from an IRC channel
===================================================================

Ircpdb is an adaptation of rpdb that, instead of opening a port and
allowing you to debug over telnet, connects to a configurable IRC
channel so you can collaboratively debug an application remotely.

.. code-block::

    import ircpdb
    ircpdb.set_trace(
        channel="#debugger_hangout",
    )

By default, ircpdb will create the channel you specify on Freenode
and randomly select a nickname for itself, but you can feel free to
configure ircpdb to connect anywhere:

.. code-block::

    import ircpdb
    ircpdb.set_trace(
        channel="#debugger_hangout",
        nickname='im_a_debugger',
        server='irc.mycompany.org',
        limit_access_to=['mynickname'],
        port=6667,
        ssl=True,
    )

Upon reaching `set_trace()`, your script will "hang" and the only way to get it
to continue is to access ircpdb by talking to the user that connected to the
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

    MyHostname: help

Installation in CPython (standard Python)
-----------------------------------------

    pip install ircpdb

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
