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

$Id: IRequestLogger.py,v 1.1 2002/11/08 14:34:58 stevea Exp $
"""

from Interface import Interface


class IRequestLogger(Interface):
    """This interface describes a requets logger, which logs
    ip addresses and messages.
    """

    def logRequest(ip, message):
        """Logs the ip address and message at the appropriate place."""
