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

$Id: UnresolvingLogger.py,v 1.2 2002/06/10 23:29:36 jim Exp $
"""
from ILogger import ILogger


class UnresolvingLogger:
    """Just in case you don't want to resolve"""

    __implements__ = ILogger

    def __init__ (self, logger):
        self.logger = logger


    ############################################################
    # Implementation methods for interface
    # Zope.Server.Logger.ILogger

    def log(self, ip, message):
        'See Zope.Server.Logger.ILogger.ILogger'
        self.logger.log ('%s: %s' % (ip, message))

    #
    ############################################################
