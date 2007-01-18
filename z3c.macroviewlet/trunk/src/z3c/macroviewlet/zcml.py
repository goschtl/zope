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
$Id$
"""
__docformat__ = "reStructuredText"

import os
from StringIO import StringIO

import zope.interface
import zope.schema
import zope.configuration.fields
from zope.configuration.exceptions import ConfigurationError
from zope.component import zcml
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.tal.talinterpreter import TALInterpreter
from zope.viewlet.interfaces import IViewlet
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet import viewlet
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


class IMacroViewletDirective(zope.interface.Interface):
    """Parameters for the template directive."""

    template = zope.configuration.fields.Path(
        title=u'Template defining a named macro.',
        description=u"""Refers to a file containing a page template 
            (should end in extension ``.pt`` or ``.html``).
            """,
        required=True,
        )

    macro = zope.schema.TextLine(
        title=u'Macro',
        description=u"""
            The name of the macro to be used. This allows us to reference 
            the named  macro defined with metal:define-macro if we use a 
            different IMacroDirective name.
            """,
        required=True,
        default=u'',
        )

    for_ = zope.configuration.fields.GlobalObject(
        title=u'Context',
        description=u'The context for which the macro should be used',
        required=False,
        default=zope.interface.Interface,
        )

    view = zope.configuration.fields.GlobalObject(
        title=u'View',
        description=u'The view for which the macro should be used',
        required=False,
        default=IBrowserView)

    manager = zope.configuration.fields.GlobalObject(
        title=u"Manager",
        description=u"The interface of the manager this provider is for.",
        required=False,
        default=IViewletManager)

    layer = zope.configuration.fields.GlobalObject(
        title=u'Layer',
        description=u'The layer for which the macro should be used',
        required=False,
        default=IDefaultBrowserLayer,
        )

    contentType = zope.schema.BytesLine(
        title=u'Content Type',
        description=u'The content type identifies the type of data.',
        default='text/html',
        required=False,
        )


class MacroViewlet(viewlet.ViewletBase):
    """Provides a single macro from a template for rendering."""

    def __init__(self, template, macroName, view, request, contentType):
        self.template = template
        self.macroName = macroName
        self.view = view
        self.request = request
        self.contentType = contentType

    def render(self):
        program = self.template.macros[self.macroName]
        output = StringIO(u'')
        namespace = self.template.pt_getContext(self.view, self.request)
        context = self.template.pt_getEngineContext(namespace)
        TALInterpreter(program, None,
                       context, output, tal=True, showtal=False,
                       strictinsert=0, sourceAnnotations=False)()
        if not self.request.response.getHeader("Content-Type"):
            self.request.response.setHeader("Content-Type",
                                            self.contentType)
        return output.getvalue()


class MacroViewletFactory(object):

    def __init__(self, filename, macro, contentType):
        self.filename = filename
        self.macro = macro
        self.contentType = contentType

    def __call__(self, context, request, view, manager):
        self.template= ViewPageTemplateFile(self.filename,
                                                content_type=self.contentType)
        return MacroViewlet(self.template, self.macro, view,
                     request, self.contentType)


def macroViewletDirective(_context, template, macro, 
    for_=zope.interface.Interface, view=IBrowserView, 
    layer=IDefaultBrowserLayer, manager=IViewletManager, 
    contentType='text/html'):

    # Make sure that the template exists
    path = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(path):
        raise ConfigurationError("No such file", template)

    factory = MacroViewletFactory(path, macro, contentType)

    # register the macro provider
    zcml.adapter(_context, (factory,), IViewlet, 
        (for_, layer, view, manager), name=macro)
