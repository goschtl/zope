##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Simple Chat room implementation.

$Id:$
"""
__docformat__ = "reStructuredText"
import persistent
from persistent.list import PersistentList
import zope.interface
from zope.location import location
from zope.schema.fieldproperty import FieldProperty

import interfaces

class ChatRoom(location.Location, persistent.Persistent):
    """See interfaces.IChatRoom."""
    zope.interface.implements(interfaces.IChatRoom)

    topic = FieldProperty(interfaces.IChatRoom['topic'])

    def __init__(self, topic):
        self.topic = topic
        self.messages = PersistentList()


    def addMessage(self, nick, message):
        self.messages.append((nick, message))
