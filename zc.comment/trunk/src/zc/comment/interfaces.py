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
"""Interfaces for comment package

$Id$
"""
import zope.interface
import zope.schema
import zope.annotation.interfaces
import zope.lifecycleevent
import zope.lifecycleevent.interfaces
from zope.interface.common.sequence import IReadSequence

from i18n import _


class ICommentText(zope.schema.interfaces.IText):
    """Type of rich text field used for comment text."""

class CommentText(zope.schema.Text):
    """Rich text field used for comment text."""
    zope.interface.implements(ICommentText)


class IComment(zope.interface.Interface):
    date = zope.schema.Datetime(
        title=_("Creation Date"),
        description=_("The date on which this comment was made"),
        required=True,
        readonly=True)

    principal_ids = zope.schema.Tuple(
        title=_("Principals"),
        description=_("""The ids of the principals who made this comment"""),
        required=True,
        readonly=True)

    body = CommentText(
        title=_("Comment Body"),
        description=_("The comment text."),
        required=False,
        readonly=True)


class IComments(IReadSequence):

    def add(body):
        """add comment with given body."""

    def clear():
        """Remove all comments."""

    def __iter__():
        """Iterate over all comments."""


class ICommentable(zope.annotation.interfaces.IAnnotatable):
    "Content that may be commented upon"


class ICommentAdded(zope.lifecycleevent.interfaces.IObjectModifiedEvent):
    """Somone added a comment to some content
    """

    comment = zope.schema.Object(
        title=u'Comment',
        description=u'The comment object that has been created.',
        schema=IComment)


class CommentAdded(zope.lifecycleevent.ObjectModifiedEvent):

    def __init__(self, object, comment):
        zope.lifecycleevent.ObjectModifiedEvent.__init__(self, object)
        self.comment = comment
