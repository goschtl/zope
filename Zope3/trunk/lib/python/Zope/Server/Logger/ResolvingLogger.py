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

$Id: ResolvingLogger.py,v 1.2 2002/06/10 23:29:36 jim Exp $
"""
from ILogger import ILogger


class ResolvingLogger:
    """Feed (ip, message) combinations into this logger to get a
    resolved hostname in front of the message.  The message will not
    be logged until the PTR request finishes (or fails)."""

    __implements__ = ILogger

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
            self.logger.log ('%s: %s' % (answer, self.message))


    ############################################################
    # Implementation methods for interface
    # Zope.Server.Logger.ILogger

    def log(self, ip, message):
        'See Zope.Server.Logger.ILogger.ILogger'
        self.resolver.resolve_ptr (
                ip,
                self.logger_thunk (
                        message,
                        self.logger
                        )
                )
    #
    ############################################################
