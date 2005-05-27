##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Renderer configuration code

$Id$
"""
from zope.app import zapi
from zope.app.component.metaconfigure import handler
from zope.configuration.fields import GlobalObject
from zope.interface import Interface

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
        args = (zapi.servicenames.Presentation, 'provideView',
                sourceType, u'', for_, factory, 'default')
        )
