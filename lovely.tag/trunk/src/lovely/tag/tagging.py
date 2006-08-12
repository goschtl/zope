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
import zope.component
import zope.interface
from zope.app import intid

from lovely.tag import interfaces

class Tagging(object):
    zope.interface.implements(interfaces.ITagging)
    zope.component.adapts(interfaces.ITaggable)

    def __init__(self, context):
        self.context = context

        ids = zope.component.getUtility(intid.interfaces.IIntIds)
        self._id = ids.queryId(self.context)
        if self._id is None:
            ids.register(self.context)
            self._id = ids.getId(self.context)

        self._engine = zope.component.getUtility(interfaces.ITaggingEngine)

    def update(self, user, tags):
        """See interfaces.ITagging"""
        return self._engine.update(self._id, user, tags)

    def getTags(self, users=None):
        """See interfaces.ITagging"""
        return self._engine.getTags(items=(self._id,), users=users)

    def getUsers(self, tags=None):
        """See interfaces.ITagging"""
        return self._engine.getUsers(items=(self._id,), tags=tags)
