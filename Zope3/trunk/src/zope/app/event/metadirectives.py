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

from zope.interface import Interface
from zope.configuration.fields import GlobalObject, Tokens

class ISubscribeDirective(Interface):
    """
    Subscribe to events
    """

    subscriber = GlobalObject(
        title=u"Subscriber",
        required=True
        )

    event_types = Tokens(
        title=u"Events to subscribe to",
        description=u"Defaults to IEvent",
        required=False,
        value_type = GlobalObject()
        )

    filter = GlobalObject(
        title=u"Filter",
        required=False
        )
