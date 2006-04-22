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

import zope.interface
import zope.formlib.interfaces
import zope.configuration.fields
import zope.configuration.exceptions
import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('zope')

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.browserzcml2.interfaces import IViewCharacteristics
from zope.browserzcml2.interfaces import IRegisterInMenu

from zope.app.publisher.browser.viewmeta import _handle_menu
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.component.metaconfigure import adapter
from zope.app.security.fields import Permission

class IPageDirective(IViewCharacteristics, IRegisterInMenu):
    """Define a browser page"""

    factory = zope.configuration.fields.GlobalObject(
        title=_(u"Factory"),
        description=_(u"Adapter factory that returns the browser page. "
                      "It should implement IPage."),
        required=True,
        )

def page(
    _context, factory,                                  # IPageDirective
    for_, name, permission, layer=IDefaultBrowserLayer, # IViewCharacteristics
    menu=None, title=None):                             # IRegisterInMenu
    if not zope.formlib.interfaces.IPage.implementedBy(factory):
        raise zope.configuration.exceptions.ConfigurationError(
            "The browser page factory needs to provide IPage. "
            "A convenient base class is zope.formlib.Page."
            )
    adapter(_context,
            factory=(factory,),
            for_=(for_, layer),
            provides=zope.formlib.interfaces.IPage,
            permission=permission,
            name=name)

    _handle_menu(_context, menu, title, (for_,), name, permission, layer)

    # emit an empty action that has the same descriminator as the
    # old-school browser:page directive handler; that way we'll get
    # proper conflicts
    _context.action(discriminator=('view', for_, name, IBrowserRequest, layer))

class IPageTemplateDirective(IViewCharacteristics, IRegisterInMenu):
    """Define a browser page from a page template"""

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
        def __getitem__(self, name):
            return self.__call__.macros[name]

    page(_context, TemplatePage,
         for_, name, permission, layer,
         menu, title)


class IPagesFromClassDirective(zope.interface.Interface):
    """Define multiple pages from a single class"""

    class_ = zope.configuration.fields.GlobalObject(
        title=_(u"Class"),
        description=_(u"A class from which one or more browser pages will "
                      "be dynamically created and registered"),
        required=True,
        )

    for_ = zope.configuration.fields.GlobalObject(
        title=_(u'Registered for'),
        description=_(u"The interface or class this view is for."),
        required=True
        )

    layer = zope.configuration.fields.GlobalInterface(
        title=_('Layer'),
        description=_("""Layer that the view is registered for.
        This defaults to IDefaultBrowserLayer."""),
        required=False,
        )

class IPageSubdirective(IRegisterInMenu):
    """Define a page based on an attribute of a class"""

    name = zope.schema.TextLine(
        title=_(u'Name'),
        description=_(u"""The name of a view, which will show up e.g. in
        URLs and other paths."""),
        required=True
        )

    permission = Permission(
        title=_(u'Permission'),
        description=_(u"The permission needed to use the view."),
        required=True
        )

    attribute = zope.configuration.fields.PythonIdentifier(
        title=_(u'Attribute'),
        description=_(u"The name of the class attribute that will be called "
                      "when the page is published the page."),
        required=True
        )

class PagesFromClass(object):

    def __init__(self, _context, class_, for_, layer=IDefaultBrowserLayer):
        self._context = _context
        self.class_ = class_
        self.for_ = for_
        self.layer = layer

    def page(self, _context, name, permission, attribute,
             menu=None, title=None):
        if attribute == '__call__':
            class PageFromClass(zope.formlib.Page, self.class_):
                pass
        else:
            class PageFromClass(zope.formlib.Page, self.class_):
                def __call__(self, *arg, **kw):
                    return getattr(self, attribute)(*arg, **kw)

        page(self._context, PageFromClass,
             self.for_, name, permission, self.layer,
             menu, title)

    def __call__(self):
        pass
