Zope 3 Monitor Server
=====================

The Zope 3 monitor server is a server that runs in a Zope 3 process
and that provides a command-line interface to request various bits of
information.  The server is zc.ngi based, so we can use the zc.ngi
testing infreastructure to demonstrate it.

    >>> import zc.ngi.testing
    >>> import zc.z3monitor
    
    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.z3monitor.Server(connection)
    
It accesses databases as utilities.  Let's create some test databases
and register them as utilities.

    >>> from ZODB.tests.util import DB
    >>> main = DB()
    >>> from zope import component
    >>> import ZODB.interfaces
    >>> component.provideUtility(main, ZODB.interfaces.IDatabase)
    >>> other = DB()
    >>> component.provideUtility(other, ZODB.interfaces.IDatabase, 'other')

We also need to able activity monitoring in the databases:

    >>> import ZODB.ActivityMonitor
    >>> main.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())
    >>> other.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())

To get information about the process overall, use the monitor
command:

    >>> connection.test_input('monitor\n')
    0 
    VmSize:	   35284 kB 
    VmRSS:	   28764 kB 
    -> CLOSE

The minimal output has:

- The number of open database connections to the main database, which
  is the database registered without a name.
- The virual memory size, and
- The resident memory size.

If there are old database connections, they will be listed.  By
default, connections are considered old if they are greater than 100
seconds old.  If you pass a value of 0, you'll see all connections.
Let's create a couple of connections and then call z2monitor again
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

The extra lone of output gine connection debug info.
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

To get information about a database, give the dbinfo command followed
by a database name:

    >>> connection.test_input('dbinfo\n')
    0   0   2 
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
    1   2   3 
    -> CLOSE

The dbinfo command returns 3 values:

- number of database loads 

- number of database stores

- number of connections in the last five minutes

You can specify a database name.  So, to get statistics for the other
database, we'll specify the name it was registered with:

    >>> connection.test_input('dbinfo other\n')
    0   0   0 
    -> CLOSE

You can use '-' to name the main database:

    >>> connection.test_input('dbinfo -\n')
    1   2   3 
    -> CLOSE

You can specify a number of seconds to sample. For example, to get
data for the last 10 seconds:

    >>> connection.test_input('dbinfo - 10\n')
    1   2   3 
    -> CLOSE

.. Edge case to make sure that deltat is used:

    >>> connection.test_input('dbinfo - 0\n')
    0   0   0 
    -> CLOSE
    
