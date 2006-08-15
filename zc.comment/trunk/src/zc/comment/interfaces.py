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
"""interfaces for comment package

$Id: interfaces.py 9472 2006-04-28 04:41:20Z gary $
"""
from zope import interface, schema
from zope.interface.common.sequence import IReadSequence
import zope.schema.interfaces

import zope.annotation.interfaces
import zope.lifecycleevent
import zope.lifecycleevent.interfaces

from zc.security.search import SimplePrincipalSource
from i18n import _


class ICommentText(schema.interfaces.IText):
    """Type of rich text field used for comment text."""

class CommentText(zope.schema.Text):
    """Rich text field used for comment text."""

    interface.implements(ICommentText)


class IComment(interface.Interface):
    date = schema.Datetime(
        title=_("Creation Date"),
        description=_("The date on which this comment was made"),
        required=True, readonly=True)

    principal_ids = schema.Tuple(
        value_type=schema.Choice(
            source=SimplePrincipalSource()),
        title=_("Principals"),
        description=_(
            """The ids of the principals who made this comment"""),
        required=True, readonly=True)

    body = CommentText(
        title=_("Comment Body"),
        description=_("The comment text."),
        required=False, readonly=True)

class IComments(IReadSequence):

    def add(body):
        """add comment with given body.
        """

    def clear():
        """Remove all comments.
        """

class ICommentable(zope.annotation.interfaces.IAnnotatable):
    "Content that may be commented upon"

class ICommentAdded(zope.lifecycleevent.interfaces.IObjectModifiedEvent):
    """Somone added a comment to some content
    """

    comment = schema.Text(title=u"The comment entered")

class CommentAdded(zope.lifecycleevent.ObjectModifiedEvent):

    def __init__(self, object, comment):
        zope.lifecycleevent.ObjectModifiedEvent.__init__(self, object)
        self.comment = comment
