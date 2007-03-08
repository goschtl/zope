# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################
"""Directive Handler for several PDF generating presentation components

$Id$
"""
__docformat__ = "reStructuredText"

import os.path

from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.publisher.browser.resourcemeta import resource
from zope.app.publisher.browser.viewmeta import page

import z3c.pdftemplate
from z3c.pdftemplate.pdf import PDFView
from z3c.pdftemplate.pml import PML2PDFView
from z3c.pdftemplate.rest import ReSTPDFResourceFactory
from z3c.pdftemplate.rml import RML2PDFView


def getTemplatePath(_context, template, default='sample/generic_template.pt'):
    """Return the path of the PDF template."""
    if template is None:
        template = os.path.join(
            os.path.dirname(z3c.pdftemplate.__file__), default)

    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)
    return template


def pdf(_context, name, permission, for_, class_,
        template=None, layer=IDefaultBrowserLayer,
        allowed_interface=None, allowed_attributes=None,
        menu=None, title=None):

    template = getTemplatePath(_context, template)

    if PDFView not in class_.__bases__:
        bases = (class_, PDFView)
    else:
        bases = (class_,)

    factory = type(
        'PDFView using template=%s' %template,
        bases, {'template': ViewPageTemplateFile(template)} )

    page(_context, name, permission, for_, layer, None, factory,
         allowed_interface, allowed_attributes, '__call__', menu, title)


def pml2pdf(_context, name, permission, for_, document,
            template=None, layer=IDefaultBrowserLayer, class_=PML2PDFView,
            allowed_interface=None, allowed_attributes=None,
            menu=None, title=None):

    template = getTemplatePath(_context, template)

    document = os.path.abspath(str(_context.path(document)))
    if not os.path.isfile(document):
        raise ConfigurationError("No such file", document)

    if class_ is not PML2PDFView and PML2PDFView not in class_.__bases__:
        bases = (class_, PML2PDFView)
    else:
        bases = (class_,)

    factory = type(
        'PML2PDFView from template=%s, document=%s' %(template, document),
        bases,
        {'template': ViewPageTemplateFile(template),
         'document': ViewPageTemplateFile(document)}
        )

    page(_context, name, permission, for_, layer, None, factory,
         allowed_interface, allowed_attributes, '__call__', menu, title)


def rest2pdf(_context, name, path,
             template=None,
             layer=IDefaultBrowserLayer, permission='zope.Public'):

    template = getTemplatePath(_context, template, 'sample/rest_template.pt')

    path = os.path.abspath(str(_context.path(path)))
    if not os.path.isfile(path):
        raise ConfigurationError("No such file", path)

    factory = ReSTPDFResourceFactory(path, ViewPageTemplateFile(template))

    resource(_context, name, layer, permission, factory)

    
def rml2pdf(_context, name, permission, for_, document,
            layer=IDefaultBrowserLayer, class_=RML2PDFView,
            allowed_interface=None, allowed_attributes=None,
            menu=None, title=None):

    document = os.path.abspath(str(_context.path(document)))
    if not os.path.isfile(document):
        raise ConfigurationError("No such file", document)

    if class_ is not RML2PDFView and RML2PDFView not in class_.__bases__:
        bases = (class_, RML2PDFView)
    else:
        bases = (class_,)

    factory = type(
        'RML2PDFView from document=%s' %(document),
        bases,
        {'document': ViewPageTemplateFile(document)}
        )

    page(_context, name, permission, for_, layer, None, factory,
         allowed_interface, allowed_attributes, '__call__', menu, title)    
