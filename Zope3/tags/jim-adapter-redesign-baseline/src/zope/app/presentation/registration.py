##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Local presentation components

$Id$
"""
__docformat__ = 'restructuredtext'

import persistent.dict

from zope.interface import implements, providedBy, Interface, Attribute
from zope.security.checker import NamesChecker, ProxyFactory
from zope.security.proxy import removeSecurityProxy

import zope.component.interfaces
import zope.configuration.exceptions
import zope.proxy
import zope.publisher.interfaces.browser

import zope.app.component.interfaces.registration
import zope.app.component.site
import zope.app.container.contained
import zope.app.interface.interfaces
import zope.app.module
from zope.app import zapi
from zope.app.dependable.interfaces import IDependable, DependencyError
from zope.app.publisher.browser import BrowserView

import interfaces


class PageRegistration(zope.app.component.site.AdapterRegistration):
    implements(interfaces.IPageRegistration)

    provided = Interface
    # We only care about browser pages
    requestType = zope.publisher.interfaces.browser.IBrowserRequest

    def __init__(self, name, required=None, permission=None,
                 factoryName=None, template=None, attribute=None):
        # An interface coming out of an interface widget is security
        # proxied which is not pickable, thus remove the proxies here
        self.required = removeSecurityProxy(required)
        self.factoryName = factoryName
        self.name = name
        self.permission = permission
        self.template = removeSecurityProxy(template)
        self.attribute = attribute
        
    def validate(self):
        if self.template and self.attribute:
            raise zope.configuration.exceptions.ConfigurationError(
                "PageRegistration for %s view name %s: "
                "Cannot have both 'template' and 'attribute' at the same "
                "time." %
                (self.required, self.name))

        if not self.template and not self.attribute:
            raise zope.configuration.exceptions.ConfigurationError(
                "PageRegistration for %s view name %s: "
                "Should have a 'template' or 'attribute' attribute." %
                (self.required, self.name))

        if not self.factoryName and self.attribute:
            raise zope.configuration.exceptions.ConfigurationError(
                "PageRegistration for %s view name %s: "
                "Cannot have an 'attribute' without a 'factoryName'." %
                (self.required, self.name))

    def with(self):
        return (self.requestType, )
    with = property(with)

    def component(self):
        self.validate()
        sm = zapi.getSiteManager(self)

        if self.factoryName:
            class_ = zope.app.module.resolve(self.factoryName, self)
        else:
            class_  = BrowserView

        if self.attribute:
            return AttributeViewFactory(class_, self.attribute)
        else:
            return TemplateViewFactory(class_, self.template, self.permission)

    component = property(component)


class Registered(object):
    """An adapter from IRegisterable to IRegistered."""
    implements(zope.app.component.interfaces.registration.IRegistered)
    __used_for__ = zope.app.component.interfaces.registration.IRegisterable

    def __init__(self, registerable):
        self.registerable = registerable

    def registrations(self):
        rm = zapi.getParent(self.registerable).registrationManager
        ICR = zope.app.component.interfaces.registration.IComponentRegistration
        return [reg for reg in rm.values()
                if (ICR.providedBy(reg) and
                    reg.template is self.registerable)]


def PageRegistrationAddSubscriber(registration, event):
    if registration.template is not None:
        dependents = IDependable(removeSecurityProxy(registration.template))
        objectpath = zapi.getPath(registration)
        dependents.addDependent(objectpath)


def PageRegistrationRemoveSubscriber(registration, event):
    if registration.template is not None:
        dependents = IDependable(removeSecurityProxy(registration.template))
        objectpath = zapi.getPath(registration)
        dependents.removeDependent(objectpath)


class TemplateViewFactory(object):
    """Factory that produces a callable template-based view."""
    def __init__(self, cls, template, permission):
        self.cls, self.template, self.permission = cls, template, permission

    def __call__(self, object, request):
        checker = NamesChecker(__call__ = self.permission)
        template = BoundTemplate(self.template, self.cls(object, request))
        return ProxyFactory(template, checker)


class AttributeViewFactory(object):
    """Factory that produces an attribute-based view."""

    def __init__(self, cls, attr):
        self.cls, self.attr = cls, attr

    def __call__(self, object, request):
        attr = getattr(self.cls(object, request), self.attr)
        return ProxyFactory(attr)


class BoundTemplate(object):

    def __init__(self, template, view):
        self.template = template
        self.view = view

    def __call__(self, *args, **kw):
        return self.template.render(self.view, *args, **kw)
