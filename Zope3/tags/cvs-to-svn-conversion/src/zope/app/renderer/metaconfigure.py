##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Renderer configuration code

$Id: metaconfigure.py,v 1.4 2003/11/21 17:10:52 jim Exp $
"""
from zope.app.component.metaconfigure import handler
from zope.app.renderer.sourcetype import SourceTypes 
from zope.configuration.fields import GlobalObject
from zope.interface import Interface
from zope.schema import TextLine
from zope.component.servicenames import Presentation

class ISourceTypeDirective(Interface):
    """The renderers directive specifies how a particular source text can
    be rendered for various view types. It also generates a registry
    of available source types."""

    interface = GlobalObject(
        title=u"Interface",
        description=u"Specifies an interface for of a particular source type.",
        required=True)

    class_ = GlobalObject(
        title=u"Class",
        description=u"Specifies the class that is implementing this " \
                     "source type.",
        required=True)

    title = TextLine(
        title=u"Title",
        description=u"Provides a title for the source type.",
        required=False)

class IRendererDirective(Interface):
    """Register a renderer for a paricular output interface, such as
    IBrowserView."""

    sourceType = GlobalObject(
        title=u"Source Type Interface",
        description=u"Specifies an interface for of a particular source type.",
        required=True)

    for_ = GlobalObject(
        title=u"Interface of the output type",
        description=u"Specifies the interface of the output type (i.e. "
                    u"browser) for which this view is being registered.",
        required=True)

    factory = GlobalObject(
        title=u"Factory",
        description=u"Specifies the factory that is used to create the "
                    u"view on the source.",
        required=True)

def renderer(_context, sourceType, for_, factory):
    _context.action(
        discriminator = ('view', sourceType, u'', for_, 'default'),
        callable = handler,
        args = (Presentation, 'provideView',
                sourceType, u'', for_, factory, 'default')
        )

def sourcetype(_context, interface, class_, title=u''):
    _context.action(
        discriminator = ('source type', title, interface),
        callable = SourceTypes.provide,
        args = (title, interface, class_)
        )
