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

$Id: unresolvinglogger.py,v 1.2 2002/12/25 14:15:27 jim Exp $
"""
from zope.server.interfaces.logger import IRequestLogger

class UnresolvingLogger:
    """Just in case you don't want to resolve"""

    __implements__ = IRequestLogger

    def __init__(self, logger):
        self.logger = logger

    def logRequest(self, ip, message):
        'See IRequestLogger'
        self.logger.logMessage('%s: %s' % (ip, message))
