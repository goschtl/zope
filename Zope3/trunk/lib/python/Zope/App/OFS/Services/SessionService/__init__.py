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

"""Session support for HTTP."""

from Zope.ComponentArchitecture import getService


def getSessionDataObject(context, request, name):
    """Get data object from appropriate ISessionDataManager."""
    service = getService(context, "SessionService")
    sid = service.getSessionId(request)
    return service.getDataManager(name).getDataObject(sid)
