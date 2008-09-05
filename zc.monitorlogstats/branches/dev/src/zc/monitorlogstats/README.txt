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

    >>> for level, count, time, message in handler.statistics:
    ...     print level, count, time
    ...     print `message`
    20 21 2008-09-05 21:11:01
    'yawn'
    30 12 2008-09-05 21:10:40
    'hm'
    40 9 2008-09-05 21:10:28
    'oops'
    50 5 2008-09-05 21:10:19
    'Yipes'

We can also ask it to clear it's statistics:

    >>> handler.clear()
    >>> for i in range(3):
    ...     logging.getLogger('foo').critical('Eek')

    >>> handler.start_time
    datetime.datetime(2008, 9, 5, 21, 11, 2)

    >>> for level, count, time, message in handler.statistics:
    ...     print level, count, time
    ...     print `message`
    50 3 2008-09-05 21:11:05
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
    ...     </counter>
    ... </logger>
    ... """))

    >>> testhandler = conf.loggers[0]().handlers[0]

    >>> for i in range(2):
    ...     logging.getLogger('test').critical('Waaa')

    >>> for level, count, time, message in handler.statistics:
    ...     print level, count, time
    ...     print `message`
    50 5 2008-09-05 21:11:10
    'Waaa'


    >>> for level, count, time, message in testhandler.statistics:
    ...     print level, count, time
    ...     print `message`
    50 2 2008-09-05 21:11:09
    'Waaa'

The example above illustrates that you can install as many counting
handlers as you want to.

.. Cleanup:

    >>> logging.getLogger().removeHandler(handler)
    >>> logging.getLogger().setLevel(logging.NOTSET)
   
    >>> logging.getLogger('test').removeHandler(testhandler)
    >>> logging.getLogger('test').setLevel(logging.NOTSET)
