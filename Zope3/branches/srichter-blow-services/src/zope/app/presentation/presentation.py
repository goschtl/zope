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

import zope.component.interfaces
import zope.configuration.exceptions
import zope.proxy
import zope.publisher.interfaces.browser

import zope.app.component.interfaces.registration
import zope.app.component.adapter
import zope.app.container.contained
import zope.app.interface.interfaces
from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.dependable.interfaces import IDependable, DependencyError

import interfaces

class GlobalViewRegistration(object):
    """Registrations representing global view thingies."""

    implements(zope.app.component.interfaces.registration.IRegistration)

    status = zope.app.component.interfaces.registration.ActiveStatus

    def __init__(self, context):
        self.context = context
        self.required = context.required[0]
        self.ptype = context.required[-1]
        self.factories = context.factory
        self.layer = context.layer
        self.viewName = context.name

    def usageSummary(self):
        if self.required is None:
            ifname = _("any-interface", "Anything")
        else:
            ifname = self.required.getName()
        summary = _("${view_name} ${ptype} View for ${iface_name}")
        if self.layer and self.layer != "default":
            summary = _(
                "${view_name} ${ptype} View for ${iface_name} in layer ${layer}"
                )
        summary.mapping = {'view_name':  self.viewName,
                           'ptype':      self.ptype.getName(),
                           'iface_name': ifname,
                           'layer':      self.layer}
        return summary

    def implementationSummary(self):
        # Report that this registration is implied because it was
        # globally defined in ZCML
        return _("Registered by ZCML")

class LocalLayer(
    zope.app.component.adapter.LocalAdapterRegistry,
    zope.app.container.contained.Contained,
    ):

    def __init__(self, base, next, parent, name):
        zope.app.adapter.LocalAdapterRegistry.__init__(
            self, base, next)
        self.__parent__ = parent
        self.__name__ = name

class ViewRegistration(zope.app.component.registration.SimpleRegistration):
    implements(interfaces.IViewRegistration)

    provided = Interface

    # For usageSummary(); subclass may override
    _what = _("view-component", 'View')

    def __init__(self,
                 required, name, requestType,
                 factoryName, permission, layer='default'):
        self.required = required
        self.requestType = requestType
        self.factoryName = factoryName
        self.name = name
        self.layer = layer
        self.permission = permission

    def usageSummary(self):
        if self.required is None:
            ifname = _('any-interface', "Anything")
        else:
            ifname = self.required.getName()

        pname = self.requestType.getName()
        summary = _("${view_name} for ${pname} ${what} ${iface_name}")
        if self.layer and self.layer != "default":
            summary = _(
                "${view_name} for ${pname} ${what} ${iface_name}"
                " in layer ${layer}"
                )
        summary.mapping = {'view_name':  self.name,
                           'pname':      pname,
                           'what':       self._what,
                           'iface_name': ifname,
                           'layer':      self.layer}
        return summary

    def with(self):
        return (self.requestType, )
    with = property(with)

    def factory(self):
        folder = self.__parent__.__parent__
        return folder.resolve(self.factoryName)
    factory = property(factory)

class PageRegistration(ViewRegistration):
    implements(interfaces.IPageRegistration)

    # We only care about browser pages
    requestType = zope.publisher.interfaces.browser.IBrowserRequest

    # For usageSummary()
    _what = _("page-component", "Page")

    def __init__(self,
                 required, name, permission,
                 factoryName=None, template=None, attribute=None,
                 layer='default'):

        # An interface coming out of an interface widget is security
        # proxied which is not pickable, thus remove the proxies here
        required = zope.proxy.removeAllProxies(required)

        super(PageRegistration, self).__init__(
            required, name, self.requestType,
            factoryName, permission, layer)

        self.template = template
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

    def factory(self):
        self.validate()
        sm = zapi.getSiteManager(self)

        if self.factoryName:
            folder = self.__parent__.__parent__
            class_ = folder.resolve(self.factoryName)
        else:
            class_  = BrowserView

        if self.attribute:
            return AttrViewFactory(class_, self.attribute)
        else:
            if self.template[0]=='/':
                # This is needed because we need to do an unrestricted zapi.
                # traverse
                root = zope.proxy.removeAllProxies(zapi.getRoot(sm))
                template = zapi.traverse(root, self.template)
            else:
                template = zapi.traverse(self.__parent__.__parent__,
                                         self.template)
            return TemplateViewFactory(class_, template, self.permission)

    factory = property(factory)

def PageRegistrationAddSubscriber(registration, event):
    if registration.template:
        template = zapi.traverse(registration.__parent__.__parent__,
                                 registration.template)
        dependents = IDependable(template)
        objectpath = zapi.getPath(registration)
        dependents.addDependent(objectpath)


def PageRegistrationRemoveSubscriber(registration, event):
    if registration.template:
        template = zapi.traverse(registration.__parent__.__parent__,
                                 registration.template)
        dependents = IDependable(template)
        objectpath = zapi.getPath(registration)
        dependents.removeDependent(objectpath)

class TemplateViewFactory(object):

    def __init__(self, cls, template, permission):
        self.cls, self.template, self.permission = cls, template, permission

        # TODO Trap code that uses 'Permissions' vocabulary instead of
        #      'Permission Ids'.  This check should go away once the mess
        #      with permissions is straigthened up.
        from zope.app.security.permission import Permission
        if isinstance(permission, Permission):
            raise TypeError('permission should be a string or CheckerPublic,'
                            ' not %r' % permission)

    def __call__(self, object, request):
        checker = NamesChecker(__call__ = self.permission)
        template = BoundTemplate(self.template, self.cls(object, request))
        return ProxyFactory(template, checker)

class AttrViewFactory(object):

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
