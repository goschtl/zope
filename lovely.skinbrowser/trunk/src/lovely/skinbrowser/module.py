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
"""Skin Browser Module

$Id$
"""
__docformat__ = 'restructuredtext'
import zope.component
import zope.interface
import zope.location

from zope.app.i18n import ZopeMessageFactory as _
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc import component, utilities
from zope.contentprovider.interfaces import IContentProvider
from zope.pagetemplate.interfaces import IPageTemplate
from zope.viewlet.interfaces import IViewlet, IViewletManager

from zope.publisher.interfaces.browser import IBrowserSkinType
from z3c.viewtemplate.interfaces import ITemplatedContentProvider

from lovely.skinbrowser import validator


def getViewPrefix(reg):
    factory = component.getRealFactory(reg.factory)
    if reg.name.endswith('html'):
        return u'Page'
    elif len(reg.required) == 3 and IViewletManager.implementedBy(factory):
        return u'Manager'
    elif len(reg.required) == 3 and IContentProvider.implementedBy(factory):
        return u'Provider'
    elif len(reg.required) == 4 and IViewlet.implementedBy(factory):
        return u'Viewlet'
    else:
        return u'View'


def getViews(spec, skin):
    """Get all views for the given skin and component spec."""
    gsm = zope.component.getGlobalSiteManager()
    result = {}
    for reg in gsm.registeredAdapters():
        factory = component.getRealFactory(reg.factory)
        if (len(reg.required) >= 2 and
            spec.isOrExtends(reg.required[0]) and
            skin.isOrExtends(reg.required[1]) and
            ITemplatedContentProvider.implementedBy(factory)
            ):
            # Make sure we pick out the most specific view
            oldidx, oldreg = result.get(reg.name, (999, None))
            newidx = list(spec.__iro__).index(reg.required[0])
            if newidx < oldidx:
                result[reg.name] = newidx, reg

    return [reg for index, reg in result.values()]


def getComponents(skin):
    """Get all components for which views are registered in the skin."""
    result = []
    gsm = zope.component.getGlobalSiteManager()
    for reg in gsm.registeredAdapters():
        factory = component.getRealFactory(reg.factory)
        if (len(reg.required) >= 2 and
            skin.isOrExtends(reg.required[1]) and
            hasattr(factory, '__implemented__') and
            ITemplatedContentProvider.implementedBy(factory) and
            reg.required[0] not in result
            ):
            result.append(reg.required[0])
    return result


def getTemplate(spec, skin):
    """Get the component for the view"""
    gsm = zope.component.getGlobalSiteManager()
    # First look up the real adapter
    factory = gsm.adapters.lookup((spec, skin), IPageTemplate)
    # Now compare factories.
    for reg in gsm.registeredAdapters():
        if reg.factory is factory:
            return reg


class Template(object):
    """Template"""
    zope.interface.implements(zope.location.ILocation)

    def __init__(self, reg, view):
        self.__parent__ = view
        self.__name__ = reg.name
        self.reg = reg

    @property
    def macro(self):
        return self.reg.factory.macro

    @property
    def filename(self):
        return self.reg.factory.filename

    @property
    def contentType(self):
        return self.reg.factory.contentType

    def validate(self):
        expressions = validator.getUsedExpressions(self.filename, self.macro)
        factory = component.getRealFactory(self.__parent__.reg.factory)
        return validator.compareExpressionsToView(expressions, factory)


class View(object):
    """View"""
    zope.interface.implements(zope.location.ILocation)

    template = None

    def __init__(self, reg, comp):
        self.__parent__ = comp
        self.__name__ = reg.name
        self.reg = reg
        factory = component.getRealFactory(reg.factory)
        treg = getTemplate(
            zope.interface.implementedBy(factory), reg.required[1])
        if treg:
            self.template = Template(treg, self)

    @property
    def title(self):
        return getViewPrefix(self.reg) + ' : ' + self.__name__


class Component(utilities.ReadContainerBase):
    """Component"""
    zope.interface.implements(zope.location.ILocation)

    def __init__(self, spec, skin):
        self.__parent__ = skin
        self.__name__ = spec.__name__
        self.spec = spec

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer"""
        return dict(self.items()).get(key, default)

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""
        results = [
            (reg.name, View(reg, self))
            for reg in getViews(self.spec, self.__parent__.interface)]
        return sorted(results, key=lambda x: x[1].title)


class Skin(utilities.ReadContainerBase):
    """Skin"""
    zope.interface.implements(zope.location.ILocation)

    def __init__(self, interface, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        self.interface = interface

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer"""
        return dict(self.items()).get(key, default)

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""
        results = [
            (spec.__name__, Component(spec, self))
            for spec in getComponents(self.interface)]
        return sorted(results)


class SkinBrowserModule(utilities.ReadContainerBase):
    """Skin Browser Module"""
    zope.interface.implements(IDocumentationModule)

    # See zope.app.apidoc.interfaces.IDocumentationModule
    title = _('Skin Browser')

    # See zope.app.apidoc.interfaces.IDocumentationModule
    description = _("""
    The skin browser allows you to inspect each skin. All views are listed and
    can be further discovered.
    """)

    def get(self, key, default=None):
        """See zope.app.container.interfaces.IReadContainer"""
        return Skin(
            zope.component.queryUtility(IBrowserSkinType, key, default=default),
            self, key)

    def items(self):
        """See zope.app.container.interfaces.IReadContainer"""
        results = [
            (name, Skin(iface, self, name))
            for name, iface in zope.component.getUtilitiesFor(IBrowserSkinType)
            # An educated guess that we really have a skin, since we cannot
            # separate them from layers anymore. Sigh.
            if '.' not in name]
        results.sort(lambda x, y: cmp(x[1].interface.getName(),
                                      y[1].interface.getName()))
        return results
