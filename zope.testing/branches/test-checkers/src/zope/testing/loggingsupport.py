##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Support for testing logging code

If you want to test that your code generates proper log output, you
can create and install a handler that collects output:

  >>> handler = InstalledHandler('foo.bar')

The handler is installed into loggers for all of the names passed. In
addition, the logger level is set to 1, which means, log
everything. If you want to log less than everything, you can provide a
level keyword argument.  The level setting effects only the named
loggers.

  >>> handler_with_levels = InstalledHandler('baz', level=logging.WARNING)

Then, any log output is collected in the handler:

  >>> logging.getLogger('foo.bar').exception('eek')
  >>> logging.getLogger('foo.bar').info('blah blah')

  >>> for record in handler.records:
  ...     print record.name, record.levelname
  ...     print ' ', record.getMessage()
  foo.bar ERROR
    eek
  foo.bar INFO
    blah blah

A similar effect can be gotten by just printing the handler:

  >>> print handler
  foo.bar ERROR
    eek
  foo.bar INFO
    blah blah

After checking the log output, you need to uninstall the handler:

  >>> handler.uninstall()
  >>> handler_with_levels.uninstall()

At which point, the handler won't get any more log output.
Let's clear the handler:

  >>> handler.clear()
  >>> handler.records
  []

And then log something:

  >>> logging.getLogger('foo.bar').info('blah')

and, sure enough, we still have no output:

  >>> handler.records
  []

$Id$
"""

import logging

from zope.testing.checkers import AbstractTestChecker


class Handler(logging.Handler):

    def __init__(self, *names, **kw):
        logging.Handler.__init__(self)
        self.names = names
        self.records = []
        self.setLoggerLevel(**kw)

    def setLoggerLevel(self, level=1):
        self.level = level
        self.oldlevels = {}

    def emit(self, record):
        self.records.append(record)

    def clear(self):
        del self.records[:]

    def install(self):
        for name in self.names:
            logger = logging.getLogger(name)
            self.oldlevels[name] = logger.level
            logger.setLevel(self.level)
            logger.addHandler(self)

    def uninstall(self):
        for name in self.names:
            logger = logging.getLogger(name)
            logger.setLevel(self.oldlevels[name])
            logger.removeHandler(self)

    def __str__(self):
        return '\n'.join(
            [("%s %s\n  %s" %
              (record.name, record.levelname,
               '\n'.join([line
                          for line in record.getMessage().split('\n')
                          if line.strip()])
               )
              )
              for record in self.records]
              )


class InstalledHandler(Handler):

    def __init__(self, *names, **kw):
        Handler.__init__(self, *names, **kw)
        self.install()


class LoggingTestChecker(AbstractTestChecker):
    """Test checker that looks for tests who register loggers and leave them."""

    what = 'the logging framework'

    def takeSnapshot(self):
        state = {}
        for name, logger in logging.root.manager.loggerDict.items():
            if isinstance(logger, logging.PlaceHolder):
                continue
            if (logger.propagate and not logger.handlers and not
                logger.disabled and logger.level == logging.NOTSET):
                # This logger is completely transparent.  Ignore it.
                # This is particularly important because the logging module has
                # no way to remove a logger other than making it transparent.
                continue
            # Remember the values of the interesting attributes, so that we
            # notice changes and not just the appearance of new loggers.
            state[name] = {'handlers': logger.handlers,
                           'propagate': logger.propagate,
                           'level': logger.level,
                           'disabled': logger.disabled}
        return state

    def showDifferences(self, old_state, new_state):
        for name in sorted(set(old_state) | set(new_state)):
            if name in old_state and name not in new_state:
                self.warn("  logger %s disappeared" % name)
            elif name in new_state and name not in old_state:
                self.warn("  new logger: %s" % name)
            else:
                attrs = [attr for attr in sorted(new_state[name])
                         if old_state[name][attr] != new_state[name][attr]]
                self.warn("  logger %s changed: %s" % (name, ', '.join(attrs)))


def test_checkers():
    """Return a list of checkers.

    The checkers can be enabled by running the test runner with
    --checkers zope.testing.loggingsupport
    """
    return [LoggingTestChecker()]

