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

$Id: UnresolvingLogger.py,v 1.3 2002/11/08 14:34:58 stevea Exp $
"""
from IRequestLogger import IRequestLogger

class UnresolvingLogger:
    """Just in case you don't want to resolve"""

    __implements__ = IRequestLogger

    def __init__(self, logger):
        self.logger = logger


    ############################################################
    # Implementation methods for interface
    # Zope.Server.Logger.IRequestLogger

    def logRequest(self, ip, message):
        'See Zope.Server.Logger.IRequestLogger.IRequestLogger'
        self.logger.logMessage('%s: %s' % (ip, message))

    #
    ############################################################
