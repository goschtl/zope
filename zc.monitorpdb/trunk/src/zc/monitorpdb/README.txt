zc.monitorpdb
=============

zc.montorpdb is a small plugin for the (very) lightweight zc.monitor
system.  It allows a user to telnet to a monitor port and invoke a
Python debugger (PDB) prompt.

To use it, one must first register the command so zc.monitor is aware of
it.

    >>> import zc.monitorpdb
    >>> import zope.component
    >>> import zc.monitor.interfaces
    >>> zope.component.provideUtility(zc.monitorpdb.command,
    ...     zc.monitor.interfaces.IMonitorPlugin, 'pdb')

Since zc.monitor is implemented with zc.ngi, we can use zc.ngi's testing
helpers.

    >>> import zc.ngi.testing
    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

If we invoke the command, we'll get the appropriate prompt.

    >>> connection.test_input('pdb\n')
    (Pdb)

Now we can do normal pdb things like list the code being executed.

    >>> connection.test_input('l\n')
     34             global fakeout
     35
     36             fakeout = FakeStdout(connection.connection)
     37             debugger = pdb.Pdb(stdin=None, stdout=fakeout)
     38             debugger.reset()
     39  ->         debugger.setup(sys._getframe(), None)
     40
     41
     42         def command(connection, *args):
     43             global debugger
     44             global fakeout
    (Pdb)

As well as go "up" in the function call stack.

    >>> connection.test_input('u\n')
    >   /zc.monitorpdb/src/zc/monitorpdb/__init__.py(48)command()
    -> reset(connection)
    (Pdb)

There is a "reset" command that gives us a fresh debugger (just in case
something bad happend to ours and we don't want to restart the host
process).  Here we go from the current location being one thing (the
result of the previous "u" command) to another.

    >>> connection.test_input('l\n')
     57                 return zc.monitor.QUIT_MARKER
     58             else:
     59                 debugger.onecmd(' '.join(args))
     60
     61             connection.write(debugger.prompt)
     62  ->         return zc.monitor.MORE_MARKER
    [EOF]
    (Pdb)
    >>> connection.test_input('reset\n')
    (Pdb)
    >>> connection.test_input('l\n')
     34             global fakeout
     35
     36             fakeout = FakeStdout(connection.connection)
     37             debugger = pdb.Pdb(stdin=None, stdout=fakeout)
     38             debugger.reset()
     39  ->         debugger.setup(sys._getframe(), None)
     40
     41
     42         def command(connection, *args):
     43             global debugger
     44             global fakeout
    (Pdb)


Some features don't work, however.

    >>> connection.test_input('debug 1+1\n')
    the "debug" command is not supported
    (Pdb)

Once we're done, we ask to be let go.

    >>> connection.test_input('quit\n')
    -> CLOSE
