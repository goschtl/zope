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

$Id: FileLogger.py,v 1.3 2002/11/08 14:34:58 stevea Exp $
"""
from types import StringType

from IMessageLogger import IMessageLogger

class FileLogger:
    """Simple File Logger
    """

    __implements__ = IMessageLogger

    def __init__(self, file, flush=1, mode='a'):
        """pass this either a path or a file object."""
        if type(file) is StringType:
            if (file == '-'):
                import sys
                self.file = sys.stdout
            else:
                self.file = open(file, mode)
        else:
            self.file = file
        self.do_flush = flush


    def __repr__(self):
        return '<file logger: %s>' % self.file


    def write(self, data):
        self.file.write(data)
        self.maybe_flush()


    def writeline(self, line):
        self.file.writeline(line)
        self.maybe_flush()


    def writelines(self, lines):
        self.file.writelines(lines)
        self.maybe_flush()


    def maybe_flush(self):
        if self.do_flush:
            self.file.flush()

    def flush(self):
        self.file.flush()

    def softspace(self, *args):
        pass


    ############################################################
    # Implementation methods for interface
    # Zope.Server.Logger.IMessageLogger

    def logMessage(self, message):
        'See Zope.Server.Logger.IMessageLogger.IMessageLogger'
        if message[-1] not in ('\r', '\n'):
            self.write(message + '\n')
        else:
            self.write(message)

    #
    ############################################################
