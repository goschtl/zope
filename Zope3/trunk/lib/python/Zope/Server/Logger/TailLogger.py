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

$Id: TailLogger.py,v 1.2 2002/06/10 23:29:36 jim Exp $
"""

from ILogger import ILogger


class TailLogger:
    """Keep track of the last <size> log messages"""

    __implements__ = ILogger

    def __init__ (self, logger, size=500):
        self.size = size
        self.logger = logger
        self.messages = []


    ############################################################
    # Implementation methods for interface
    # Zope.Server.Logger.ILogger

    def log(self, message):
        'See Zope.Server.Logger.ILogger.ILogger'
        self.messages.append (strip_eol (message))
        if len (self.messages) > self.size:
            del self.messages[0]
        self.logger.log (message)

    #
    ############################################################


def strip_eol (line):
    while line and line[-1] in '\r\n':
        line = line[:-1]
    return line
