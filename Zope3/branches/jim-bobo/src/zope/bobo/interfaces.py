##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Bobo interfaces

$Id$
"""

import zope.interface

class IPublicationEvent(zope.interface.Interface):

    request = zope.interface.Attribute('Request being published')

class IObjectPublicationEvent(IPublicationEvent):

    object = zope.interface.Attribute('Object being published')

class PublicationEvent(object):

    zope.interface.implements(IPublicationEvent)

    def __init__(self, request):
        self.request = request

class ObjectPublicationEvent(object):

    zope.interface.implements(IObjectPublicationEvent)

    def __init__(self, request, object):
        self.request = request
        self.object = object

class BeginRequest(PublicationEvent):
    "A request started"

class BeforeTraverse(ObjectPublicationEvent):
    "We are about to traverse an object"

class AfterTraversal(ObjectPublicationEvent):
    "We are finished with object traversal"

class AfterCall(ObjectPublicationEvent):
    "We called an objevt without error"

class PublicationException(object):
    "A call failed"

    def __init__(self, request, object, exc_info, retry_allowed):
        self.request = request
        self.object = object
        self.exc_info = exc_info
        self.retry_allowed = retry_allowed

class EndRequest(ObjectPublicationEvent):
    "A request ended"
