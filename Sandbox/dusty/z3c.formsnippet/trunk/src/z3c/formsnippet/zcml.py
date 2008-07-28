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
$Id: zcml.py 75940 2007-05-24 14:45:00Z srichter $
"""
__docformat__ = "reStructuredText"

import os

import zope.interface
import zope.component.zcml
import zope.schema
import zope.configuration.fields
from zope.configuration.exceptions import ConfigurationError
from zope.pagetemplate.interfaces import IPageTemplate
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from z3c.form import interfaces
from z3c.form.i18n import MessageFactory as _
from z3c.formsnippet import FormframeTemplateFactory, SnippetTemplateFactory
from z3c.formsnippet import ErrorstatusTemplateFactory
from z3c.formsnippet.interfaces import IFormframeTemplate, IErrorstatusTemplate


class IFormframeTemplateDirective(zope.interface.Interface):
    """Parameters for the Formframe template directive."""

    template = zope.configuration.fields.Path(
        title=_('Form frame template.'),
        description=_('Refers to a file containing a page template (should '
                      'end in extension ``.pt`` or ``.html``).'),
        required=True)

    for_ = zope.configuration.fields.GlobalObject(
        title=_('View'),
        description=_('The view for which the template should be available'),
        default=zope.interface.Interface,
        required = False)

    layer = zope.configuration.fields.GlobalObject(
        title=_('Layer'),
        description=_('The layer for which the template should be available'),
        default=IDefaultBrowserLayer,
        required=False)

    contentType = zope.schema.BytesLine(
        title=_('Content Type'),
        description=_('The content type identifies the type of data.'),
        default='text/html',
        required=False)

def formframeTemplateDirective(
    _context, template, for_=zope.interface.Interface,
    layer=IDefaultBrowserLayer, contentType='text/html'):

    # Make sure that the template exists
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    factory = FormframeTemplateFactory(template, contentType)
    zope.interface.directlyProvides(factory, IFormframeTemplate)

    # register the template
    zope.component.zcml.adapter(_context, (factory,), IFormframeTemplate,
        (for_, layer))


class IErrorstatusTemplateDirective(zope.interface.Interface):
    """Parameters for the Formframe template directive."""

    template = zope.configuration.fields.Path(
        title=_('Errorstatus template.'),
        description=_('Refers to a file containing a page template (should '
                      'end in extension ``.pt`` or ``.html``).'),
        required=True)

    for_ = zope.configuration.fields.GlobalObject(
        title=_('View'),
        description=_('The view for which the template should be available'),
        default=zope.interface.Interface,
        required = False)

    layer = zope.configuration.fields.GlobalObject(
        title=_('Layer'),
        description=_('The layer for which the template should be available'),
        default=IDefaultBrowserLayer,
        required=False)

    contentType = zope.schema.BytesLine(
        title=_('Content Type'),
        description=_('The content type identifies the type of data.'),
        default='text/html',
        required=False)

def errorstatusTemplateDirective(
    _context, template, for_=zope.interface.Interface,
    layer=IDefaultBrowserLayer, contentType='text/html'):

    # Make sure that the template exists
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    factory = ErrorstatusTemplateFactory(template, contentType)
    zope.interface.directlyProvides(factory, IErrorstatusTemplate)

    # register the template
    zope.component.zcml.adapter(_context, (factory,), IErrorstatusTemplate,
        (for_, layer))



class ISnippetTemplateDirective(zope.interface.Interface):
    """Parameters for the snippet template directive."""

    template = zope.configuration.fields.Path(
        title=_('Layout template.'),
        description=_('Refers to a file containing a page template (should '
                      'end in extension ``.pt`` or ``.html``).'),
        required=True)

    name = zope.schema.BytesLine(
        title=_('The name of the snippet'),
        description=_('The snippet name that can be used in page templates'),
        required=True)

    mode = zope.schema.BytesLine(
        title=_('The mode of the template.'),
        description=_('The mode is used for define input and display '
                      'templates'),
        default=interfaces.INPUT_MODE,
        required=False)

    for_ = zope.configuration.fields.GlobalObject(
        title=_('View'),
        description=_('The view for which the template should be available'),
        default=zope.interface.Interface,
        required = False)

    layer = zope.configuration.fields.GlobalObject(
        title=_('Layer'),
        description=_('The layer for which the template should be available'),
        default=IDefaultBrowserLayer,
        required=False)

    view = zope.configuration.fields.GlobalObject(
        title=_('View'),
        description=_('The view for which the template should be available'),
        default=zope.interface.Interface,
        required=False)

    field = zope.configuration.fields.GlobalObject(
        title=_('Field'),
        description=_('The field for which the template should be available'),
        default=zope.schema.interfaces.IField,
        required=False)

    widget = zope.configuration.fields.GlobalObject(
        title=_('View'),
        description=_('The widget for which the template should be available'),
        default=interfaces.IWidget,
        required=False)

    contentType = zope.schema.BytesLine(
        title=_('Content Type'),
        description=_('The content type identifies the type of data.'),
        default='text/html',
        required=False)

def snippetTemplateDirective(
    _context, template, for_=zope.interface.Interface,
    layer=IDefaultBrowserLayer, view=None, field=None, widget=None,
    name='', mode=interfaces.INPUT_MODE, contentType='text/html'):

    # Make sure that the template exists
    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    factory = SnippetTemplateFactory(template, contentType)
    zope.interface.directlyProvides(factory, IPageTemplate)

    # register the template
    zope.component.zcml.adapter(_context, (factory,), IPageTemplate,
        (for_, layer, view, field, widget), name=name+'_'+mode)



