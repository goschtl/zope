##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""Simple comments implementation as an annotation to commentable objects.

$Id$
"""
import datetime
import persistent
import persistent.list
import pytz
import zope.annotation.interfaces
import zope.component
import zope.event
import zope.interface
import zope.location
import zope.security.management
import zope.publisher.interfaces
from zope.schema.fieldproperty import FieldProperty
from zope.annotation import factory

from zc.comment import interfaces

class Comment(zope.location.Location, persistent.Persistent):
    zope.interface.implements(interfaces.IComment)
    body = FieldProperty(interfaces.IComment['body'])
    date = FieldProperty(interfaces.IComment['date'])
    principal_ids = FieldProperty(interfaces.IComment['principal_ids'])

    def __init__(self, body):
        self.body = body
        self.date = datetime.datetime.now(pytz.utc)
        interaction = zope.security.management.getInteraction()
        self.principal_ids = tuple(
            [p.principal.id for p in interaction.participations
             if zope.publisher.interfaces.IRequest.providedBy(p)])


class Comments(zope.location.Location, persistent.list.PersistentList):
    zope.interface.implements(interfaces.IComments)
    zope.component.adapts(interfaces.ICommentable)

    def pop(self):
        raise AttributeError
    pop = property(pop)
    __setitem__ = __delitem__ = __setslice__ = __delslice__ = __iadd__ = pop
    insert = append = remove = reverse = sort = extend = pop

    def add(self, body):
        comment = Comment(body)
        super(Comments, self).append(comment)
        zope.event.notify(interfaces.CommentAdded(self.__parent__, comment))

    def clear(self):
        persistent.list.PersistentList.__init__(self)

    def __repr__(self):
        return '<%s (%i) for %r>' %(
            self.__class__.__name__, len(self), self.__parent__)


CommentsFactory = factory(Comments)
