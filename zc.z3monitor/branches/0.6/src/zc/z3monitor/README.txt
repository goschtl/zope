=====================
Zope 3 Monitor Server
=====================

The Zope 3 monitor server is a server that runs in a Zope 3 process
and that provides a command-line interface to request various bits of
information.  The server is zc.ngi based, so we can use the zc.ngi
testing infrastructure to demonstrate it.

    >>> import zc.ngi.testing
    >>> import zc.z3monitor

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.z3monitor.Server(connection)

The server supports an extensible set of commands.  It looks up
commands as named zc.z3monitor.interfaces.IZ3MonitorPlugin plugins.

To see this, we'll create a hello plugin:

    >>> def hello(connection, name='world'):
    ...     """Say hello
    ...     
    ...     Provide a name if you're not the world.
    ...     """
    ...     connection.write("Hi %s, nice to meet ya!\n" % name) 

and register it:

    >>> import zope.component, zc.z3monitor.interfaces
    >>> zope.component.provideUtility(
    ...   hello, zc.z3monitor.interfaces.IZ3MonitorPlugin, 'hello')

Now we can give the hello command to the server:

    >>> connection.test_input('hello\n')
    Hi world, nice to meet ya!
    -> CLOSE

We can pass a name:

    >>> connection.test_input('hello Jim\n')
    Hi Jim, nice to meet ya!
    -> CLOSE

The server comes with a number of useful commands.  Let's register
them so we can see what they do:

    >>> zope.component.provideUtility(zc.z3monitor.help,
    ...     zc.z3monitor.interfaces.IZ3MonitorPlugin, 'help')
    >>> zope.component.provideUtility(zc.z3monitor.interactive,
    ...     zc.z3monitor.interfaces.IZ3MonitorPlugin, 'interactive')
    >>> zope.component.provideUtility(zc.z3monitor.quit,
    ...     zc.z3monitor.interfaces.IZ3MonitorPlugin, 'quit')
    >>> zope.component.provideUtility(zc.z3monitor.monitor,
    ...     zc.z3monitor.interfaces.IZ3MonitorPlugin, 'monitor')
    >>> zope.component.provideUtility(zc.z3monitor.dbinfo,
    ...     zc.z3monitor.interfaces.IZ3MonitorPlugin, 'dbinfo')
    >>> zope.component.provideUtility(zc.z3monitor.zeocache,
    ...     zc.z3monitor.interfaces.IZ3MonitorPlugin, 'zeocache')
    >>> zope.component.provideUtility(zc.z3monitor.zeostatus,
    ...     zc.z3monitor.interfaces.IZ3MonitorPlugin, 'zeostatus')

The first is the help command.  Giving help without input, gives a
list of available commands:

    >>> connection.test_input('help\n')
    Supported commands:
      dbinfo -- Get database statistics
      hello -- Say hello
      help -- Get help about server commands
      interactive -- Turn on monitor's interactive mode
      monitor -- Get general process info
      quit -- Quit the monitor
      zeocache -- Get ZEO client cache statistics
      zeostatus -- Get ZEO client status information
    -> CLOSE

We can get detailed help by specifying a command name:

    >>> connection.test_input('help help\n')
    Help for help:
    <BLANKLINE>
    Get help about server commands
    <BLANKLINE>
        By default, a list of commands and summaries is printed.  Provide
        a command name to get detailed documentation for a command.
    <BLANKLINE>
    -> CLOSE

    >>> connection.test_input('help hello\n')
    Help for hello:
    <BLANKLINE>
    Say hello
    <BLANKLINE>
        Provide a name if you're not the world.
    <BLANKLINE>
    -> CLOSE

The ``interactive`` command switches the monitor into interactive mode.  As
seen above, the monitor usually responds to a single command and then closes
the connection.  In "interactive mode", the connection is not closed until
the ``quit`` command is used.  This can be useful when accessing the monitor
via telnet for diagnostics.

    >>> connection.test_input('interactive\n')
    Interactive mode on.  Use "quit" To exit.
    >>> connection.test_input('help interactive\n')
    Help for interactive:
    <BLANKLINE>
    Turn on monitor's interactive mode
    <BLANKLINE>
        Normally, the monitor releases the connection after a single command.
        By entering the interactive mode, the monitor will not end the connection
        until you enter the "quit" command.
    <BLANKLINE>
    >>> connection.test_input('help quit\n')
    Help for quit:
    <BLANKLINE>
    Quit the monitor
    <BLANKLINE>
        This is only really useful in interactive mode (see the "interactive"
        command).
    <BLANKLINE>
    >>> connection.test_input('quit\n')
    Goodbye.
    -> CLOSE

The other commands that come with the monitor use database information.  
They access databases as utilities.  Let's create some test databases
and register them as utilities.

    >>> from ZODB.tests.util import DB
    >>> main = DB()
    >>> from zope import component
    >>> import ZODB.interfaces
    >>> component.provideUtility(main, ZODB.interfaces.IDatabase)
    >>> other = DB()
    >>> component.provideUtility(other, ZODB.interfaces.IDatabase, 'other')

We also need to enable activity monitoring in the databases:

    >>> import ZODB.ActivityMonitor
    >>> main.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())
    >>> other.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())

Process Information
===================

To get information about the process overall, use the monitor
command:

    >>> connection.test_input('help monitor\n')
    Help for monitor:
    <BLANKLINE>
    Get general process info
    <BLANKLINE>
        The minimal output has:
    <BLANKLINE>
        - The number of open database connections to the main database, which
          is the database registered without a name.
        - The virtual memory size, and
        - The resident memory size.
    <BLANKLINE>
        If there are old database connections, they will be listed.  By
        default, connections are considered old if they are greater than 100
        seconds old. You can pass a minimum old connection age in seconds.
        If you pass a value of 0, you'll see all connections.
    <BLANKLINE>
        If you pass a name after the integer, this is used as the database name.
        The database name defaults to the empty string ('').
    <BLANKLINE>
    -> CLOSE

    >>> connection.test_input('monitor\n')
    0 
    VmSize:	   35284 kB 
    VmRSS:	   28764 kB 
    -> CLOSE

    >>> connection.test_input('monitor 100 other\n')
    0 
    VmSize:	   35284 kB 
    VmRSS:	   28764 kB 
    -> CLOSE

Note that, as of this writing, the VmSize and VmRSS lines will only be present
on a system with procfs.  This generally includes many varieties of Linux,
and excludes OS X and Windows.

Let's create a couple of connections and then call z3monitor again
with a value of 0:

    >>> conn1 = main.open()
    >>> conn2 = main.open()

    >>> connection.test_input('monitor 0\n')
    2 
    VmSize:	   36560 kB 
    VmRSS:	   28704 kB 
    0.0    (0) 
    0.0    (0) 
    -> CLOSE

The extra line of output gives connection debug info.
If we set some additional input, we'll see it:

    >>> conn1.setDebugInfo('/foo')
    >>> conn2.setDebugInfo('/bar')

    >>> connection.test_input('monitor 0\n')
    2 
    VmSize:	   13048 kB 
    VmRSS:	   10084 kB 
    0.0   /bar (0) 
    0.0   /foo (0) 
    -> CLOSE

    >>> conn1.close()
    >>> conn2.close()

Database Information
====================

To get information about a database, use the dbinfo command:

    >>> connection.test_input('help dbinfo\n')
    Help for dbinfo:
    <BLANKLINE>
    Get database statistics
    <BLANKLINE>
        By default statistics are returned for the main database.  The
        statistics are returned as a single line consisting of the:
    <BLANKLINE>
        - number of database loads
    <BLANKLINE>
        - number of database stores
    <BLANKLINE>
        - number of connections in the last five minutes
    <BLANKLINE>
        - number of objects in the object caches (combined)
    <BLANKLINE>
        - number of non-ghost objects in the object caches (combined)
    <BLANKLINE>
        You can pass a database name, where "-" is an alias for the main database.
    <BLANKLINE>
        By default, the statistics are for a sampling interval of 5
        minutes.  You can request another sampling interval, up to an
        hour, by passing a sampling interval in seconds after the database name.    
    <BLANKLINE>
    -> CLOSE

    >>> connection.test_input('dbinfo\n')
    0   0   2   0   0 
    -> CLOSE

Let's open a connection and do some work:

    >>> conn = main.open()
    >>> conn.root()['a'] = 1
    >>> import transaction
    >>> transaction.commit()
    >>> conn.root()['a'] = 1
    >>> transaction.commit()
    >>> conn.close()

    >>> connection.test_input('dbinfo\n')
    1   2   3   1   1 
    -> CLOSE

You can specify a database name.  So, to get statistics for the other
database, we'll specify the name it was registered with:

    >>> connection.test_input('dbinfo other\n')
    0   0   0   0   0 
    -> CLOSE

You can use '-' to name the main database:

    >>> connection.test_input('dbinfo -\n')
    1   2   3   1   1 
    -> CLOSE

You can specify a number of seconds to sample. For example, to get
data for the last 10 seconds:

    >>> connection.test_input('dbinfo - 10\n')
    1   2   3   1   1 
    -> CLOSE

.. Edge case to make sure that ``deltat`` is used:

    >>> connection.test_input('dbinfo - 0\n')
    0   0   0   1   1 
    -> CLOSE

ZEO cache statistics
====================

You can get ZEO cache statistics using the zeocache command.

    >>> connection.test_input('help zeocache\n')
    Help for zeocache:
    <BLANKLINE>
    Get ZEO client cache statistics
    <BLANKLINE>
        The command returns data in a single line:
    <BLANKLINE>
        - the number of records added to the cache,
    <BLANKLINE>
        - the number of bytes added to the cache,
    <BLANKLINE>
        - the number of records evicted from the cache,
    <BLANKLINE>
        - the number of bytes evicted from the cache,
    <BLANKLINE>
        - the number of cache accesses.
    <BLANKLINE>
        By default, data for the main database are returned.  To return
        information for another database, pass the database name.
    <BLANKLINE>
    -> CLOSE

    >>> connection.test_input('zeocache\n')
    42 4200 23 2300 1000 
    -> CLOSE

You can specify a database name:

    >>> connection.test_input('zeocache other\n')
    42 4200 23 2300 1000 
    -> CLOSE

ZEO Cache status
================

The zeostatus command lets you get information about ZEO connection status:

    >>> connection.test_input('help zeostatus\n')
    Help for zeostatus:
    <BLANKLINE>
    Get ZEO client status information
    <BLANKLINE>
        The command returns True if the client is connected and False otherwise.
    <BLANKLINE>
        By default, data for the main database are returned.  To return
        information for another database, pass the database name.
    <BLANKLINE>
    -> CLOSE

    >>> connection.test_input('zeostatus\n')
    True 
    -> CLOSE

    >>> connection.test_input('zeostatus other\n')
    True 
    -> CLOSE

In this example, we're using a faux ZEO connection.  It has an
attribute that determines whether it is connected or not.  Id we
change it, then the zeocache output will change:

    >>> main._storage._is_connected = False
    >>> connection.test_input('zeostatus\n')
    False 
    -> CLOSE

