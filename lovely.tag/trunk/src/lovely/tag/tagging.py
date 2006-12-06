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
from zope.cachedescriptors.property import Lazy
from zope.security.management import getInteraction
from lovely.tag import interfaces


class Tagging(object):
    zope.interface.implements(interfaces.ITagging)
    zope.component.adapts(interfaces.ITaggable)

    engineName = ''

    def __init__(self, context):
        self.context = context

    @Lazy
    def docId(self):
        ids = zope.component.getUtility(intid.interfaces.IIntIds,
                                        context=self.context)
        id = ids.queryId(self.context)
        if id is None:
            ids.register(self.context)
            id = ids.getId(self.context)
        return id

    @Lazy
    def engine(self):
        return zope.component.getUtility(interfaces.ITaggingEngine,
                                         context=self.context,
                                         name=self.engineName)

    def update(self, user, tags):
        """See interfaces.ITagging"""
        try:
            self.engine.update(self.docId, user, tags)
        except zope.component.ComponentLookupError:
            # special behaviour :
            #  If we update without tags it is possible that we do this
            #  because an object has been deleted. This is usually done in an
            #  event handler for ObjectRemovedEvent. If we would raise an
            #  exeption in this case it is not possible to delete a site.
            if tags:
                raise

    def getTags(self, users=None):
        """See interfaces.ITagging"""
        return self.engine.getTags(items=(self.docId,), users=users)

    def getUsers(self, tags=None):
        """See interfaces.ITagging"""
        return self.engine.getUsers(items=(self.docId,), tags=tags)


class UserTagging(object):
    zope.interface.implements(interfaces.IUserTagging)
    zope.component.adapts(interfaces.ITaggable)

    engineName = ''

    def __init__(self, context):
        self.context = context

    @Lazy
    def docId(self):
        ids = zope.component.getUtility(intid.interfaces.IIntIds)
        id = ids.queryId(self.context)
        if id is None:
            ids.register(self.context)
            id = ids.getId(self.context)
        return id

    @Lazy
    def engine(self):
        return zope.component.getUtility(interfaces.ITaggingEngine,
                                         name=self.engineName)

    @property
    def _pid(self):
        participations = getInteraction().participations
        if participations:
            return participations[0].principal.id
        else:
            raise ValueError, "User not found"

    @apply
    def tags():
        def fget(self):
            return self.engine.getTags(items=(self.docId,),
                                        users=(self._pid,))
        def fset(self, value):
            if value is None:
                return
            try:
                self.engine.update(self.docId, self._pid, value)
            except zope.component.ComponentLookupError:
                # special behaviour :
                #  If we update without tags it is possible that we do this
                #  because an object has been deleted. This is usually done in an
                #  event handler for ObjectRemovedEvent. If we would raise an
                #  exeption in this case it is not possible to delete a site.
                if value:
                    raise
        return property(**locals())

