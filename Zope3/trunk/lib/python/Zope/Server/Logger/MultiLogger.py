##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: MultiLogger.py,v 1.2 2002/06/10 23:29:36 jim Exp $
"""

import asynchat
import socket
import time         # these three are for the rotating logger
import os           # |
import stat         # v

from types import StringType


class MultiLogger:
    """Log to multiple places."""

    def __init__ (self, loggers):
        self.loggers = loggers

    def __repr__ (self):
        return '<multi logger: %s>' % (repr(self.loggers))

    def log (self, message):
        for logger in self.loggers:
            logger.log (message)



class ResolvingLogger:
    """Feed (ip, message) combinations into this logger to get a
    resolved hostname in front of the message.  The message will not
    be logged until the PTR request finishes (or fails)."""

    def __init__ (self, resolver, logger):
        self.resolver = resolver
        self.logger = logger


    class logger_thunk:
        def __init__ (self, message, logger):
            self.message = message
            self.logger = logger

        def __call__ (self, host, ttl, answer):
            if not answer:
                answer = host
            self.logger.log ('%s%s' % (answer, self.message))


    def log (self, ip, message):
        self.resolver.resolve_ptr (
                ip,
                self.logger_thunk (
                        message,
                        self.logger
                        )
                )



class UnresolvingLogger:
    """Just in case you don't want to resolve"""
    def __init__ (self, logger):
        self.logger = logger

    def log (self, ip, message):
        self.logger.log ('%s%s' % (ip, message))


def strip_eol (line):
    while line and line[-1] in '\r\n':
        line = line[:-1]
    return line


class TailLogger:
    """Keep track of the last <size> log messages"""
    def __init__ (self, logger, size=500):
        self.size = size
        self.logger = logger
        self.messages = []

    def log (self, message):
        self.messages.append (strip_eol (message))
        if len (self.messages) > self.size:
            del self.messages[0]
        self.logger.log (message)
