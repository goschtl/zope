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
"""Local presentation service

$Id$
"""
import persistent.dict

from zope.interface import implements, providedBy, Interface, Attribute
from zope.security.checker import NamesChecker, ProxyFactory
from zope.component.presentation import IDefaultViewName
from zope.component.presentation import PresentationRegistration

import zope.app.container.contained
import zope.app.registration.interfaces
import zope.app.site.interfaces
import zope.app.adapter
import zope.app.interface.interfaces
import zope.component.interfaces
import zope.component.presentation
import zope.configuration.exceptions
import zope.proxy
import zope.publisher.interfaces.browser
import zope.schema

from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.dependable.interfaces import IDependable, DependencyError
from zope.app.registration.interfaces import IRegistered

# TODO: Skins and layer definitions are not handled by this service
# but left up to services above, which effectively means the global
# service.  This problem will probably become obsolete when the
# ImplementViewsAsAdapters proposal is implemented.

class LocalPresentationService(
    zope.app.adapter.LocalAdapterBasedService,
    ):

    implements(
        zope.component.interfaces.IPresentationService,
        zope.app.site.interfaces.ISimpleService,
        zope.app.registration.interfaces.IRegistry,
        zope.app.interface.interfaces.IInterfaceBasedRegistry,
        )

    next = base = None

    def __init__(self):
        self.layers = persistent.dict.PersistentDict()
        self.base = zapi.getGlobalService(zapi.servicenames.Presentation)

    def setNext(self, next, global_):
        if next is None:
            self.delegate = global_
        else:
            self.delegate = next
            
        self.next = next
        self.base = global_
        for layername in self.layers:
            nextlayer = next.queryLayer(layername)
            globlayer = global_.queryLayer(layername)
            self.layers[layername].setNext(nextlayer, globlayer)

    def defaultSkin(self):
        return self.delegate.defaultSkin
    defaultSkin = property(defaultSkin)

    def querySkin(self, name):
        return self.delegate.querySkin(name)

    def queryLayer(self, name):
        r = self.layers.get(name)
        if r is not None:
            return r
        return self.delegate.queryLayer(name)

    def queryView(self, object, name, request,
                  providing=Interface, default=None):
        """Look for a named view for a given object and request

        The request must implement IPresentationRequest.

        The default will be returned if the component can't be found.
        """
        skin = request.getPresentationSkin() or self.defaultSkin
        layers = self.querySkin(skin)
        if not layers:
            return default
        
        objects = object, request
        for layername in layers:
            layer = self.layers.get(layername)
            if layer is None:
                layer = self.delegate.queryLayer(layername)
                if layer is None:
                    raise ValueError("Bad layer", layer)

            r = layer.queryMultiAdapter(objects, providing, name)
            if r is not None:
                return r
        return default

    def queryResource(self, name, request, providing=Interface,
                      default=None):
        """Look up a named resource for a given request
        
        The request must implement IPresentationRequest.
        
        The default will be returned if the component can't be found.
        """
        skin = request.getPresentationSkin() or self.defaultSkin
        layers = self.querySkin(skin)
        if not layers:
            return default

        for layername in layers:
            layer = self.layers.get(layername)
            if layer is None:
                layer = self.delegate.queryLayer(layername)
            if layer is None:
                raise ValueError("Bad layer", layer)

            r = layer.queryAdapter(request, providing, name)
            if r is not None:
                return r

        return default

    def queryMultiView(self, objects, request,
                       providing=Interface, name='',
                       default=None):
        """Adapt the given objects and request

        The first argument is a sequence of objects to be adapted with the
        request.
        """

        skin = request.getPresentationSkin() or self.defaultSkin
        layers = self.querySkin(skin)
        if not layers:
            return default

        objects = objects + (request, )
        for layername in layers:
            layer = self.layers.get(layername)
            if layer is None:
                layer = self.delegate.queryLayer(layername)
            if layer is None:
                raise ValueError("Bad layer", layer)

            r = layer.queryMultiAdapter(objects, providing, name)
            if r is not None:
                return r
        return default

    def queryDefaultViewName(self, object, request, default=None):
        skin = request.getPresentationSkin() or self.defaultSkin
        layers = self.querySkin(skin)
        if not layers:
            return default

        objects = object, request
        for layername in layers:
            layer = self.layers.get(layername)
            if layer is None:
                layer = self.delegate.queryLayer(layername)
            if layer is None:
                raise ValueError("Bad layer", layer)
            r = layer.lookup(map(providedBy, objects),
                             IDefaultViewName)
            if r is not None:
                return r
        return default

    def queryRegistrationsFor(self, registration, default=None):
        layername = registration.layer
        layer = self.layers.get(layername)
        if layer is None:
            return default
        return layer.queryRegistrationsFor(registration, default)

    def createRegistrationsFor(self, registration):
        layername = registration.layer
        layer = self.layers.get(layername)
        if layer is None:
            if self.next is None:
                next = None
            else:
                next = self.next.queryLayer(layername)
            base = self.base.queryLayer(layername)
            if base is None:
                raise ValueError("Undefined layer", layername)
            layer = LocalLayer(base, next, self, layername)
            self.layers[layername] = layer
            
        return layer.createRegistrationsFor(registration)

    def registrations(self, localOnly=False):
        for layer in self.layers.itervalues():
            for registration in layer.registrations():
                yield registration

        if localOnly is True:
            return

        next = self.next
        if next is None:
            next = self.base

        for registration in next.registrations():
            yield registration

    def getRegistrationsForInterface(self, required):
        iro = required.__iro__ + (None,)

        for registration in self.registrations():
            if IViewRegistration.providedBy(registration):
                if registration.required in iro:
                    yield registration

            if isinstance(registration, PresentationRegistration):
                if registration.required[0] in iro:
                    # Not using an adapter here, since it would be just
                    # overhead.
                    yield GlobalViewRegistration(registration)                

class GlobalViewRegistration(object):
    """Registrations representing global view service thingies."""

    implements(zope.app.registration.interfaces.IRegistration)

    serviceType = zapi.servicenames.Presentation
    status = zope.app.registration.interfaces.ActiveStatus

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
    zope.app.adapter.LocalAdapterRegistry,
    zope.app.container.contained.Contained,
    ):

    def __init__(self, base, next, parent, name):
        zope.app.adapter.LocalAdapterRegistry.__init__(
            self, base, next)
        self.__parent__ = parent
        self.__name__ = name

class IViewRegistration(zope.app.adapter.IAdapterRegistration):

    required = zope.schema.Choice(
        title = _(u"For interface"),
        description = _(u"The interface of the objects being viewed"),
        vocabulary="Interfaces",
        readonly = True,
        required = True,
        )

    requestType = zope.schema.Choice(
        title = _(u"Request type"),
        description = _(u"The type of requests the view works with"),
        vocabulary="Interfaces",
        readonly = True,
        required = True,
        )

    layer = zope.schema.BytesLine(
        title = _(u"Layer"),
        description = _(u"The skin layer the view is registered for"),
        required = False,
        readonly = True,
        min_length = 1,
        default = "default",
        )

class ViewRegistration(zope.app.registration.registration.SimpleRegistration):
    implements(IViewRegistration)

    serviceType = zapi.servicenames.Presentation
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

class IPageRegistration(IViewRegistration):

    factoryName = zope.schema.BytesLine(
        title=_(u"Page class"),
        required = False,
        )

    template = zope.app.registration.interfaces.ComponentPath(
        title = _(u"Page template"),
        required = False,
        )

    attribute = zope.schema.TextLine(
        title = _(u"Class attribute"),
        required = False,
        )

    factory = Attribute(
        _("Factory to be called to construct an adapter")
        )

    def validate(self):
        """Verifies that the registration is valid.

        Raises a ConfigurationError if the validation is failed.
        """

class PageRegistration(ViewRegistration):
    implements(IPageRegistration)

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

    def implementationSummary(self):
        L = []
        if self.template:
            prefix = "/++etc++site/"
            t = self.template
            i = t.rfind(prefix)
            if i >= 0:
                t = t[i + len(prefix):]
            L.append("template=%s" % t)
        if self.factoryName:
            L.append("class=%s" % self.factoryName)
        if self.attribute:
            L.append("attribute=%s" % self.attribute)
        return ", ".join(L)

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
        sm = zapi.getServices(self)

        if self.factoryName:
            folder = self.__parent__.__parent__
            class_ = folder.resolve(self.factoryName)
        else:
            class_  = DefaultClass

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

def PageRegistrationAddSubscriber(self, event):
    if self.template:
        template = zapi.traverse(self.__parent__.__parent__,self.template)
        dependents = IDependable(template)
        objectpath = zapi.getPath(self)
        dependents.addDependent(objectpath)


def PageRegistrationRemoveSubscriber(self, event):
    if self.template:
        template = zapi.traverse(self.__parent__.__parent__,self.template)
        dependents = IDependable(template)
        objectpath = zapi.getPath(self)
        dependents.removeDependent(objectpath)

# TODO: Make this a new-style class. This is not easily possible
# because existing databases apparently contain references to
# instances of this class; probably because of a difference in the
# pickling protocol, we get an UnpicklingError if we simply make this
# a newstyle class.
class TemplateViewFactory:

    def __init__(self, cls, template, permission):
        self.cls, self.template, self.permission = cls, template, permission

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

class DefaultClass(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

class BoundTemplate(object):

    def __init__(self, template, view):
        self.template = template
        self.view = view

    def __call__(self, *args, **kw):
        return self.template.render(self.view, *args, **kw)
