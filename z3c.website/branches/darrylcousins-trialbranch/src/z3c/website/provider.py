##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
$Id: provider.py 72087 2007-01-18 01:03:33Z rogerineichen $
"""

import zope.interface
import zope.component
from zope.publisher.interfaces import browser
from zope.pagetemplate.interfaces import IPageTemplate

from z3c.pagelet import interfaces


class SamplePageletRenderer(object):
    """Render the adapted pagelet including the summary and author."""

    zope.interface.implements(interfaces.IPageletRenderer)

    def __init__(self, context, request, pagelet):
        self.__updated = False
        self.__parent__ = pagelet
        self.context = context
        self.request = request

    def update(self):
        pass

    def render(self):
        intro = self.introTemplate()
        content = self.__parent__.render()
        footer = self.footerTemplate()
        return intro + content + footer

    def introTemplate(self):
        """This template renders the intro for you into your sample template.
        
        You dont have to do anything else. All the maigic get done by the 
        custom z3c.pagelet.interfaces.IPageletRenderer.
        """
        template = zope.component.getMultiAdapter((self.__parent__, 
            self.request), IPageTemplate, name='intro')
        return template(self.__parent__)

    def footerTemplate(self):
        """This template renders the footer info for you into your sample 
        template.
        
        You dont have to do anything else. All the maigic get done by the 
        custom z3c.pagelet.interfaces.IPageletRenderer.
        """
        template = zope.component.getMultiAdapter((self.__parent__, 
            self.request), IPageTemplate, name='footer')
        return template(self.__parent__)
