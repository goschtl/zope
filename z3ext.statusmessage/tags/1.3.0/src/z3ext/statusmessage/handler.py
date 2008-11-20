##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" 

$Id$
"""
from threading import local
from zope import interface, component
from zope.app.publication.zopepublication import ZopePublication

from interfaces import IStatusMessage


# BAD! VERY BAD

def newAfterCall(self, request, ob):
    response = request.response

    status = response.getStatus()
    if status not in (302, 303):
        service = IStatusMessage(request, None)
        if service is None:
            return

        messages = service.clear()

        if messages:
            body = response.consumeBody()
            body = body.replace(
                '<!--z3ext-statusmessage-->', str(u'\n'.join(messages)), 1)
            response.setResult(body)

    afterCall(self, request, ob)

afterCall = ZopePublication.afterCall
ZopePublication.afterCall = newAfterCall
