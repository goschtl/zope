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

$Id: TailLogger.py,v 1.3 2002/11/08 14:34:58 stevea Exp $
"""

from IMessageLogger import IMessageLogger

class TailLogger:
    """Keep track of the last <size> log messages"""

    __implements__ = IMessageLogger

    def __init__(self, logger, size=500):
        self.size = size
        self.logger = logger
        self.messages = []


    ############################################################
    # Implementation methods for interface
    # Zope.Server.Logger.IMessageLogger

    def logMessage(self, message):
        'See Zope.Server.Logger.IMessageLogger.IMessageLogger'
        self.messages.append(strip_eol(message))
        if len(self.messages) > self.size:
            del self.messages[0]
        self.logger.logMessage(message)

    #
    ############################################################


def strip_eol(line):
    while line and line[-1] in '\r\n':
        line = line[:-1]
    return line
