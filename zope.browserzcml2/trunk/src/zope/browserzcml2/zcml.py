##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""ZCML directives and their handlers

$Id$
"""
__docformat__ = "reStructuredText"

import zope.configuration.fields
import zope.configuration.exceptions
import zope.formlib
import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('zope')

from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.browserzcml2.interfaces import IViewCharacteristics
from zope.browserzcml2.interfaces import IRegisterInMenu

from zope.app.publisher.browser.viewmeta import _handle_menu
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.component.metaconfigure import adapter

class IPageTemplateDirective(IViewCharacteristics, IRegisterInMenu):

    template = zope.configuration.fields.Path(
        title=_(u"Template"),
        description=_(u"""
        Refers to a file containing a page template (should end in
        extension '.pt' or '.html')."""),
        required=True
        )

def pageTemplate(
    _context, template,                                 # IPageTemplateDirective
    for_, name, permission, layer=IDefaultBrowserLayer, # IViewCharacteristics
    menu=None, title=None):                             # IRegisterInMenu

    class TemplatePage(zope.formlib.Page):
        __call__ = ViewPageTemplateFile(template)

    page(_context, TemplatePage,
         for_, name, permission, layer,
         menu, title)

class IPageDirective(IViewCharacteristics, IRegisterInMenu):
    """Define multiple pages without repeating all of the parameters.

    The pages directive allows multiple page views to be defined
    without repeating the 'for', 'permission', 'class', 'layer',
    'allowed_attributes', and 'allowed_interface' attributes.
    """

    factory = zope.configuration.fields.GlobalObject(
        title=_(u"Factory"),
        description=_(u"Adapter factory that returns the browser page. "
                      "It should implement IBrowserPublisher."),
        required=True,
        )

def page(
    _context, factory,                                  # IPageDirective
    for_, name, permission, layer=IDefaultBrowserLayer, # IViewCharacteristics
    menu=None, title=None):                             # IRegisterInMenu
    if not IBrowserPublisher.implementedBy(factory):
        raise zope.configuration.exceptions.ConfigurationError(
            "The browser page factory needs to provide IBrowserPublisher. "
            "A convenient base class is zope.formlib.Page."
            )
    adapter(_context,
            factory=(factory,),
            for_=(for_, layer),
            provides=IBrowserPublisher,
            permission=permission,
            name=name)

    _handle_menu(_context, menu, title, (for_,), name, permission, layer)

class IPagesFromClassDirective(IViewCharacteristics):
    """Define multiple pages without repeating all of the parameters.

    The pages directive allows multiple page views to be defined
    without repeating the 'for', 'permission', 'class', 'layer',
    'allowed_attributes', and 'allowed_interface' attributes.
    """

    class_ = zope.configuration.fields.GlobalObject(
        title=_(u"Class"),
        description=_(u"A class from which one or more browser pages will "
                      "be dynamically created and registered"),
        required=False,
        )

# XXX PagesFromClass
