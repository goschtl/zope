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

$Id: CommonFTPActivityLogger.py,v 1.3 2002/11/08 14:34:58 stevea Exp $
"""

import time
import sys

from Zope.Server.Logger.FileLogger import FileLogger
from Zope.Server.Logger.ResolvingLogger import ResolvingLogger
from Zope.Server.Logger.UnresolvingLogger import UnresolvingLogger

class CommonFTPActivityLogger:
    """Outputs hits in common HTTP log format.
    """

    def __init__(self, logger_object=None, resolver=None):
        if logger_object is None:
            logger_object = FileLogger(sys.stdout)

        if resolver is not None:
            self.output = ResolvingLogger(resolver, logger_object)
        else:
            self.output = UnresolvingLogger(logger_object)


    def log(self, task):
        """
        Receives a completed task and logs it in the
        common log format.
        """

        now = time.localtime(time.time())

        message = '%s [%s] "%s %s"' % (task.channel.username,
                                       time.strftime('%Y/%m/%d %H:%M', now),
                                       task.m_name[4:].upper(),
                                       task.channel.cwd,
                                       )

        self.output.logRequest('127.0.0.1', message)
