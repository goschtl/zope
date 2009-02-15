##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Event Interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Attribute
from zope.interface import implements
from zope.interface import Interface
from zope.component.interfaces import IObjectEvent

class IBeforeTraverseEvent(IObjectEvent):
    """An event which gets sent on publication traverse"""

    request = Attribute("The current request")

class BeforeTraverseEvent(object):
    """An event which gets sent on publication traverse"""

    implements(IBeforeTraverseEvent)

    def __init__(self, ob, request):
        self.object = ob
        self.request = request


class IEndRequestEvent(Interface):
    """An event which gets sent when the publication is ended"""


class EndRequestEvent(object):
    """An event which gets sent when the publication is ended"""

    implements(IEndRequestEvent)

    def __init__(self, ob, request):
        self.object = ob
        self.request = request
