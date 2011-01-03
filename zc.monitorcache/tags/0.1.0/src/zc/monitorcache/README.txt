zc.monitorcache
===============

zc.montorcache is a zc.z3monitor plugin that allows one to modify or check
the cache size (in objects or bytes) of a running instance.

    >>> import zc.monitorcache
    >>> import zope.component
    >>> import zc.ngi.testing
    >>> import zc.monitor
    >>> import zc.monitor.interfaces
    >>> import zc.z3monitor
    >>> import zc.z3monitor.interfaces

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

    >>> zope.component.provideUtility(zc.monitorcache.cacheMonitor,
    ...     zc.z3monitor.interfaces.IZ3MonitorPlugin, 'cache_size')

    >>> connection.test_input('cache_size\n')
    -> CLOSE

We have no databases right now. Let's add a few so that we can test.

    >>> import ZODB.tests.util
    >>> import ZODB.interfaces
    >>> main = ZODB.tests.util.DB()
    >>> zope.component.provideUtility(main, ZODB.interfaces.IDatabase)
    >>> test = ZODB.tests.util.DB()
    >>> zope.component.provideUtility(
    ...     test, ZODB.interfaces.IDatabase, 'test')

Now we should get information on each of the database's cache sizes

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

    >>> connection.test_input('cache_size\n')
    DB cache sizes for main
    Max objects: 400
    Max object size bytes: 0MB
    DB cache sizes for test
    Max objects: 400
    Max object size bytes: 0MB
    -> CLOSE

We can request information about a specific db as well

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

    >>> connection.test_input('cache_size -\n')
    DB cache sizes for main
    Max objects: 400
    Max object size bytes: 0MB
    -> CLOSE

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

    >>> connection.test_input('cache_size test\n')
    DB cache sizes for test
    Max objects: 400
    Max object size bytes: 0MB
    -> CLOSE

We can also modify cache sizes for a specific db

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

    >>> connection.test_input('cache_size test 300\n')
    Set max objects to 300
    -> CLOSE

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

    >>> connection.test_input('cache_size test 10MB\n')
    Set max object size bytes to 10MB
    -> CLOSE

    >>> connection = zc.ngi.testing.TextConnection()
    >>> server = zc.monitor.Server(connection)

    >>> connection.test_input('cache_size test\n')
    DB cache sizes for test
    Max objects: 300
    Max object size bytes: 10MB
    -> CLOSE
