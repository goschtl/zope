##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""An adapter from IPrincipal to the ILoggingInfo.

$Id: principallogging.py,v 1.1 2003/07/22 15:09:35 ryzaja Exp $
"""

from zope.interface import implements
from zope.publisher.interfaces.logginginfo import ILoggingInfo

class PrincipalLogging:

    implements(ILoggingInfo)

    def __init__(self, principal):
        self.principal = principal

    def getLogMessage(self):
        return str(self.principal.getId())
