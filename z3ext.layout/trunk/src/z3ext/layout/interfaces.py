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
""" z3ext.layout interfaces

$Id$
"""
from zope import interface
from zope.publisher.interfaces.browser import IBrowserPage


class IPagelet(IBrowserPage):
    """ pagelet """

    isRedirected = interface.Attribute('is redirected')

    def redirect(url=''):
        """Redirect URL, if `update` method needs redirect,
        it should call `redirect` method, __call__ method should
        check isRendered before render or layout."""

    def update():
        """Update the pagelet data."""

    def render():
        """Render the pagelet content w/o o-wrap."""


class ILayout(IBrowserPage):
    """ layout """

    title = interface.Attribute('Layout title')

    description = interface.Attribute('Layout description')

    template = interface.Attribute('Layout template')

    def update():
        """Update the layout data """

    def render():
        """Render the layout """


class ILayoutTemplateFile(interface.Interface):
    """ layout template file """


class ILayoutCreatedEvent(interface.Interface):
    """ notification about new layout """

    name = interface.Attribute('Name')

    view = interface.Attribute('View')

    context = interface.Attribute('Context')

    layer = interface.Attribute('Layer')

    layoutclass = interface.Attribute('Generated class for layout')

    keywords = interface.Attribute('Keywords')
