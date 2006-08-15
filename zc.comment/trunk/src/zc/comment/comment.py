##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""comment adapter

$Id: comment.py 9472 2006-04-28 04:41:20Z gary $
"""
import datetime, UserList, pytz

from persistent.list import PersistentList
from zope import interface, component, event
import zope.annotation.interfaces
import zope.security.management
import zope.publisher.interfaces

from zc.comment import interfaces

marker = 'zc.comment'

class Comment(object):
    interface.implements(interfaces.IComment)

    def __init__(self, body):
        if not isinstance(body, unicode):
            raise ValueError("comment body must be unicode")
        self.body = body
        self.date = datetime.datetime.now(pytz.utc)
        interaction = zope.security.management.getInteraction()
        self.principal_ids = tuple(
            [p.principal.id for p in interaction.participations
             if zope.publisher.interfaces.IRequest.providedBy(p)])

class Comments(object, UserList.UserList):
    interface.implements(interfaces.IComments)
    component.adapts(interfaces.ICommentable)
    def pop(self):
        raise AttributeError
    pop = property(pop)
    __setitem__ = __delitem__ = __setslice__ = __delslice__ = __iadd__ = pop
    insert = append = remove = reverse = sort = extend = pop

    def __init__(self, context):
        self.__parent__ = context # so we can acquire grants
        self.context = context
        self.annotations = zope.annotation.interfaces.IAnnotations(
            self.context)
        self.data = self.annotations.get(marker)
        if self.data is None:
            self.data = []
    
    def add(self, body):
        if self.annotations.get(marker) is None:
            self.data = self.annotations[marker] = PersistentList()
        self.data.append(Comment(body))
        event.notify(interfaces.CommentAdded(self.context, body))

    def clear(self): # XXX no test
        if marker in self.annotations:
            del self.annotations[marker]
        
