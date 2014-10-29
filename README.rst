ircpdb - Remotely debug your Python application from an IRC channel
===================================================================

.. warning::

   This library is a work in progress and is, as of yet, non-functional.
   Give me a few days.

ircpdb is an adaptation of rpdb that, instead of opening a port and
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
        port=6667
    )

Upon reaching `set_trace()`, your script will "hang" and the only way to get it
to continue is to access ircpdb by talking to the user that connected to the
above IRC channel.

Installation in CPython (standard Python)
-----------------------------------------

    pip install ircpdb

Author(s)
---------
Adam Coddington <me@adamcoddington.net> - http://adamcoddington.net/

This library is a fork of rpdb, and the underpinnings of this library
are owed to Bertrand Janin <b@janin.com> - http://tamentis.com/.

With contributions from (chronological, latest first):

 - Ken Manheimer - @kenmanheimer
 - Steven Willis - @onlynone
 - Jorge Niedbalski R <niedbalski@gmail.com>
 - Cyprien Le Pannérer <clepannerer@edd.fr>
 - k4ml <kamal.mustafa@gmail.com>
 - Sean M. Collins <sean@coreitpro.com>

This is inspired by:

 - http://bugs.python.org/issue721464
 - http://snippets.dzone.com/posts/show/7248
