##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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

from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass

from zope.interface import implements, Interface
from zope.schema import TextLine, List
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('formtest')

class IContent(Interface):

    title = TextLine(
        title=_(u"Title"),
        description=_(u"A short description of the event."),
        default=u"",
        required=True
        )

    somelist = List(
        title=_(u"Some List"),
        value_type=TextLine(title=_(u"Some item")),
        default=[],
        required=False
        )

class Content(SimpleItem):
    """A Viewable piece of content with fields
    """
    implements(IContent)
    
    meta_type = 'Five Formlib Test Content'

    def __init__(self, id, title, somelist=None):
        self.id = id
        self.title = title
        self.somelist = somelist

InitializeClass(Content)
        