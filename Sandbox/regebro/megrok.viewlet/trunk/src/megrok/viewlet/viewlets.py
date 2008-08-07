##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Interfaces
"""
from zope import component
from zope.interface import implements
from zope.publisher.publish import mapply
import grok

import interfaces
from meta import Viewlet, ViewletManager

class TitleViewletManager(ViewletManager):
    grok.name('title')
    # Implements AND provides? Can I get rid of one?
    implements(interfaces.ITitle)
    grok.provides(interfaces.ITitle)


class TitleViewlet(Viewlet):
    # Should this be like grok.viewlet_manager(ILeftColumn) instead?
    viewlet_manager = interfaces.ITitle

    def render(self):
        return getattr(self.context, 'title', u'')


class ContentViewletManager(ViewletManager):
    grok.name('main_content')
    # Implements AND provides? Can I get rid of one?
    implements(interfaces.IMainContent)
    grok.provides(interfaces.IMainContent)


class ContentViewlet(Viewlet):
    viewlet_manager = interfaces.IMainContent

    def render(self):
        return mapply(self.view, 
                      self.request.getPositionalArguments(), 
                      self.request)

