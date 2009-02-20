Logger Monitor
==============

The zc.loggermonitor package provides a zc.monitor plugin for getting
and setting logger levels.

    >>> import sys, zc.loggermonitor

It is an error to call the monitor without user arguments.

    >>> zc.loggermonitor.level(sys.stdout)
    Traceback (most recent call last):
    ...
    TypeError: level() takes at least 2 arguments (1 given)

If you pass it a logger name, it returns the current effective level:

    >>> zc.loggermonitor.level(sys.stdout, '.')
    NOTSET
    >>> zc.loggermonitor.level(sys.stdout, 'mylogger')
    NOTSET

If you pass a level it sets the level:

    >>> zc.loggermonitor.level(sys.stdout, '.', 'INFO')

    >>> zc.loggermonitor.level(sys.stdout, '.')
    INFO
    >>> zc.loggermonitor.level(sys.stdout, 'mylogger')
    INFO

You can also pass a numeric value:

    >>> zc.loggermonitor.level(sys.stdout, 'mylogger', '5')
    >>> zc.loggermonitor.level(sys.stdout, '.')
    INFO
    >>> zc.loggermonitor.level(sys.stdout, 'mylogger')
    Level 5

    >>> zc.loggermonitor.level(sys.stdout, 'mylogger', '10')
    >>> zc.loggermonitor.level(sys.stdout, '.')
    INFO
    >>> zc.loggermonitor.level(sys.stdout, 'mylogger')
    DEBUG

    >>> zc.loggermonitor.level(sys.stdout, 'mylogger', 'NOTSET')
    >>> zc.loggermonitor.level(sys.stdout, '.')
    INFO
    >>> zc.loggermonitor.level(sys.stdout, 'mylogger')
    INFO

    >>> zc.loggermonitor.level(sys.stdout, '.', 'NOTSET')
    >>> zc.loggermonitor.level(sys.stdout, '.')
    NOTSET
    >>> zc.loggermonitor.level(sys.stdout, 'mylogger')
    NOTSET
