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

$Id$
"""

from zope.interface import implements, Interface
from zope.app.event.interfaces import IEvent


class IPublicationRequestFactoryFactory(Interface):
    """Publication request factory factory"""

    def realize(db):
        """Create a publication and request factory for a given database

        Return a IPublicationRequestFactory for the given database.
        """


class IPublicationRequestFactory(Interface):
    """Publication request factory"""

    def __call__(input_stream, output_steam, env):
        """Create a request object to handle the given inputs

        A request is created and configured with a publication object.
        """


class IRequestFactory(IPublicationRequestFactory,
                      IPublicationRequestFactoryFactory):
    """This is a pure read-only interface, since the values are set through
       a ZCML directive and we shouldn't be able to change them.
    """


class IBeforeTraverseEvent(IEvent):
    """An event which gets sent on publication traverse"""


class BeforeTraverseEvent:
    """An event which gets sent on publication traverse"""
    implements(IBeforeTraverseEvent)
    def __init__(self, ob, request):
        self.object = ob
        self.request = request


class IEndRequestEvent(IEvent):
    """An event which gets sent when the publication is ended"""


class EndRequestEvent:
    """An event which gets sent when the publication is ended"""
    implements(IEndRequestEvent)
    def __init__(self, ob, request):
        self.object = ob
        self.request = request
