##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Tag Implementation

$Id$
"""
__docformat__ = "reStructuredText"

import datetime
import persistent
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from lovely.tag import interfaces

def normalizeTagName(name):
    return name.lower()

class Tag(persistent.Persistent):
    """Simple implementation of a tag."""
    zope.interface.implements(interfaces.ITag)

    item = FieldProperty(interfaces.ITag['item'])
    user = FieldProperty(interfaces.ITag['user'])
    name = FieldProperty(interfaces.ITag['name'])
    timestamp = FieldProperty(interfaces.ITag['timestamp'])
    
    def __init__(self, item, user, name):
        self.item = item
        if not isinstance(user, unicode):
            user = unicode(user, 'utf-8')
        self.user = user
        self.name = name
        self.timestamp = datetime.datetime.now()

    def __cmp__(self, other):
        return cmp((self.item, self.user, self.name),
                   (other.item, other.user, other.name))

    def __repr__(self):
        return '<%s %r for %i by %r>' %(
            self.__class__.__name__, self.name, self.item, self.user)
