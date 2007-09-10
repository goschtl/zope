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
"""
$Id$
"""
__docformat__ = "reStructuredText"

import datetime
import persistent
import zope.interface
from zope.app.container import contained

from lovely.rating import IRating
from pytz import UTC

class Rating(contained.Contained, persistent.Persistent):
    zope.interface.implements(IRating)

    id = property(lambda self: self._id)
    value = property(lambda self: self._value)
    user = property(lambda self: self._user)
    timestamp = property(lambda self: self._timestamp)

    def __init__(self, id, value, user):
        self._id = id
        self._value = value
        self._user = user
        self._timestamp = datetime.datetime.now(UTC)

    def __repr__(self):
        return '<%s %r by %r>' %(self.__class__.__name__, self.value, self.user)

    def __cmp__(self, other):
        if not isinstance(other, Rating):
            return cmp(super(Rating, self), other)
        return cmp((self.id, self.value, self.user),
                   (other.id, other.value, other.user))

