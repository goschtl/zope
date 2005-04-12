##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pagelet Demo

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface

from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Choice

from zope.i18n import MessageIDFactory
_ = MessageIDFactory('zope')

from zope.app.pagelet.interfaces import IPageletSlot
from zope.app.pagelet.interfaces import IPageData



class IPageletContent(Interface):
    """A sample content type for to test pagelet."""

    title = TextLine(
        title=_(u"Title"),
        description=_(u"Title of the sample"),
        default=u"",
        required=False)
    
    description = Text(
        title=_(u"Description"),
        description=_(u"Description of the sample"),
        default=u"",
        required=False)



class IDemoSlot(IPageletSlot):
    """Demo pagelet slot interface for to lookup pagelets."""



class IDemoPageData(IPageData):
    """Demo page data adapter interface."""
