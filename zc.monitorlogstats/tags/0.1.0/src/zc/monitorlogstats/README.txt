zc.z3monitor plugin and log handler for getting Log statistics
==============================================================

zc.monitorlogstats provides a zc.z3monitor plugin and log handler to
track log statistics.  The idea is that you can conect to it to find
out how many log entries of various types have been posted. If you
sample it over time, youcan see how many entries are added.  In
particular, if you get new warning, error, or critical entries,
someone might want to look at the logs to find out what's going on.

Counting Log Handler
--------------------

Let's start by looking at the log handler.  The factory
zc.monitorlogstats.CountingHandler can be installed like any other
handler.  It doesn't emit anything. It just counts.

Let's create one to see how it works:

    >>> import logging, zc.monitorlogstats
    >>> handler = zc.monitorlogstats.CountingHandler()
    >>> logging.getLogger().addHandler(handler)
    >>> logging.getLogger().setLevel(logging.INFO)

Now, let's log:

    >>> for i in range(5):
    ...     logging.getLogger('foo').critical('Yipes')

    >>> for i in range(9):
    ...     logging.getLogger('bar').error('oops')

    >>> for i in range(12):
    ...     logging.getLogger('baz').warn('hm')

    >>> for i in range(21):
    ...     logging.getLogger('foo').info('yawn')

    >>> for i in range(99):
    ...     logging.getLogger('xxx').log(5, 'yuck yuck')

We can ask the handler for statistics:

    >>> handler.start_time
    datetime.datetime(2008, 9, 5, 21, 10, 14)

    >>> for level, count, message in handler.statistics:
    ...     print level, count
    ...     print `message`
    20 21
    'yawn'
    30 12
    'hm'
    40 9
    'oops'
    50 5
    'Yipes'

The statistics consist of the log level, the count of log messages,
and the formatted text of last message.

We can also ask it to clear it's statistics:

    >>> handler.clear()
    >>> for i in range(3):
    ...     logging.getLogger('foo').critical('Eek')

    >>> handler.start_time
    datetime.datetime(2008, 9, 5, 21, 10, 15)

    >>> for level, count, message in handler.statistics:
    ...     print level, count
    ...     print `message`
    50 3
    'Eek'

There's ZConfig support for defining counting handlers:

    >>> import ZConfig, StringIO
    >>> schema = ZConfig.loadSchemaFile(StringIO.StringIO("""
    ... <schema>
    ...  <import package="ZConfig.components.logger"/>
    ...  <multisection type="logger" attribute="loggers" name="*" required="no">
    ...  </multisection>
    ... </schema>
    ... """))

    >>> conf, _ = ZConfig.loadConfigFile(schema, StringIO.StringIO("""
    ... %import zc.monitorlogstats
    ... <logger>
    ...     name test
    ...     level INFO
    ...     <counter>
    ...        format %(name)s %(message)s
    ...     </counter>
    ... </logger>
    ... """))

    >>> testhandler = conf.loggers[0]().handlers[0]

    >>> for i in range(2):
    ...     logging.getLogger('test').critical('Waaa')
    >>> for i in range(22):
    ...     logging.getLogger('test.foo').info('Zzzzz')

    >>> for level, count, message in handler.statistics:
    ...     print level, count
    ...     print `message`
    20 22
    'Zzzzz'
    50 5
    'Waaa'

    >>> for level, count, message in testhandler.statistics:
    ...     print level, count
    ...     print `message`
    20 22
    'test.foo Zzzzz'
    50 2
    'test Waaa'

Note that the message output from the test handler reflects the format
we used when we set it up. 

The example above illustrates that you can install as many counting
handlers as you want to.

Monitor Plugin
--------------

The zc.monitorlogstats Monitor plugin can be used to query log statistics.

    >>> import sys
    >>> plugin = zc.monitorlogstats.monitor(sys.stdout)
    2008-09-05T21:10:15
    20 22 'Zzzzz'
    50 5 'Waaa'

The output consists of the start time and line for each log level for
which there are statistics.  Each statistics line has the log level,
entry count, and a repr of the last log message.

By default, the root logger will be used. You can specify a logger name:

    >>> plugin = zc.monitorlogstats.monitor(sys.stdout, 'test')
    2008-09-05T21:10:16
    20 22 'test.foo Zzzzz'
    50 2 'test Waaa'

You can use '.' for the root logger:

    >>> plugin = zc.monitorlogstats.monitor(sys.stdout, '.')
    2008-09-05T21:10:15
    20 22 'Zzzzz'
    50 5 'Waaa'

Note that if there are multiple counting handlers for a logger, only
the first will be used. (So don't define more than one. :)

It is an error to name a logger without a counting handler:

    >>> plugin = zc.monitorlogstats.monitor(sys.stdout, 'test.foo')
    Traceback (most recent call last):
    ...
    ValueError: Invalid logger name: test.foo

You can specify a second argument with a value of 'clear', ro clear
statistics:

    >>> plugin = zc.monitorlogstats.monitor(sys.stdout, 'test', 'clear')
    2008-09-05T21:10:16
    20 22 'test.foo Zzzzz'
    50 2 'test Waaa'

    >>> plugin = zc.monitorlogstats.monitor(sys.stdout, 'test', 'clear')
    2008-09-05T21:10:17

.. Edge case:
 
    >>> plugin = zc.monitorlogstats.monitor(sys.stdout, 'test', 'yes')
    Traceback (most recent call last):
    ...
    ValueError: The second argument, if present, must have the value 'clear'.
   

.. Cleanup:

    >>> logging.getLogger().removeHandler(handler)
    >>> logging.getLogger().setLevel(logging.NOTSET)
   
    >>> logging.getLogger('test').removeHandler(testhandler)
    >>> logging.getLogger('test').setLevel(logging.NOTSET)
