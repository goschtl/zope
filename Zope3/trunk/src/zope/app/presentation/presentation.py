##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Local presentation service

$Id: presentation.py,v 1.5 2004/03/13 15:21:26 srichter Exp $
"""
import persistent.dict
from zope.app import zapi
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.component.presentation import IDefaultViewName
from zope.security.checker import NamesChecker, ProxyFactory

import zope.app.component.interfacefield
import zope.app.component.nextservice
import zope.app.container.contained
import zope.app.interfaces.services.registration
import zope.app.site.interfaces
import zope.app.adapter
import zope.app.services.field
import zope.app.interface.interfaces
import zope.app.adapter
import zope.component.interfaces
import zope.configuration.exceptions
import zope.interface
import zope.proxy
import zope.publisher.interfaces.browser
import zope.schema
from zope.app.container.interfaces import IAddNotifiable
from zope.app.interfaces.dependable import IDependable, DependencyError
from zope.app.interfaces.services.registration import IRegistered

# XXX How do we define skins and layers here?
# For now, we will leave skin and layer definition to services above,
# which effectively means to the global service.

class LocalPresentationService(
    zope.app.adapter.LocalAdapterBasedService,
    ):

    zope.interface.implements(
        zope.component.interfaces.IPresentationService,
        zope.app.site.interfaces.ISimpleService,
        zope.app.interfaces.services.registration.IRegistry,
        zope.app.interface.interfaces.IInterfaceBasedRegistry,
        )

    next = base = None

    def __init__(self):
        self.layers = persistent.dict.PersistentDict()
        self.base = zapi.getService(None, zapi.servicenames.Presentation)

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
                  providing=zope.interface.Interface, default=None):
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


    def queryResource(self, name, request, providing=zope.interface.Interface,
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

            r = layer.queryNamedAdapter(request, providing,
                                        name)
            if r is not None:
                return r

        return default

    def queryMultiView(self, objects, name, request,
                       providing=zope.interface.Interface, default=None):
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
            r = layer.queryMultiAdapter(objects, IDefaultViewName, raw=True)
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

    def getRegistrationsForInterface(self, required):
        # XXX relying on global service for layer definitions

        iro = required.__iro__ + (None,)
        for layername in self.base._layers:
            layer = self.queryLayer(layername)
            if isinstance(layer, LocalLayer):
                while layer is not None:
                    for iface in iro:
                        stacks = layer.stacks.get(iface)
                        if not stacks:
                            continue
                        for stack in stacks.itervalues():
                            registration = stack.active()
                            if registration is not None:
                                yield registration
                    layer = layer.next
                layer = self.base.queryLayer(layername)
            if layer is None:
                continue

            for (req, provided, with, name, factories
                 ) in layer.getRegisteredMatching(required=required):
                # XXX just do views for now. We need a more general
                # solution
                if len(with) == 1:
                    yield GlobalViewRegistration(req, with[0], factories,
                                                 layername, name)
                    
                

class GlobalViewRegistration:
    """Registrations representing global view service thingies."""

    zope.interface.implements(
        zope.app.interfaces.services.registration.IRegistration)

    serviceType = zapi.servicenames.Presentation
    status = zope.app.interfaces.services.registration.ActiveStatus

    def __init__(self, req, ptype, factories, layer, viewName):
        self.required = req
        self.ptype = ptype
        self.factories = factories
        self.layer = layer
        self.viewName = viewName

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
        # XXX This should report the ZCML that it came from.
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

    required = zope.app.component.interfacefield.InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being viewed",
        readonly = True,
        required = True,
        basetype = None
        )

    requestType = zope.app.component.interfacefield.InterfaceField(
        title = u"Request type",
        description = u"The type of requests the view works with",
        readonly = True,
        required = True,
        )

    layer = zope.schema.BytesLine(
        title = u"Layer",
        description = u"The skin layer the view is registered for",
        required = False,
        readonly = True,
        min_length = 1,
        default = "default",
        )

class ViewRegistration(zope.app.services.registration.SimpleRegistration):

    zope.interface.implements(IViewRegistration)

    serviceType = zapi.servicenames.Presentation

    provided = zope.interface.Interface

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
        summary = _("${view_name} for ${pname} {what} {iface_name}")
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

    def factories(self):
        folder = self.__parent__.__parent__
        return (folder.resolve(self.factoryName), )
    factories = property(factories)

class IPageRegistration(IViewRegistration):

    factoryName = zope.schema.BytesLine(
        title=u"Page class",
        required = False,
        )

    template = zope.app.interfaces.services.registration.ComponentPath(
        title = u"Page template",
        required = False,
        )

    attribute = zope.schema.TextLine(
        title = u"Class attribute",
        required = False,
        )

    factories = zope.interface.Attribute(
        "A sequence of factories to be called to construct an adapter"
        )

    def validate(self):
        """Verifies that the registration is valid.

        Raises a ConfigurationError if the validation is failed.
        """

class PageRegistration(ViewRegistration):

    zope.interface.implements(IPageRegistration, IAddNotifiable)

    # We only care about browser pages
    requestType = zope.publisher.interfaces.browser.IBrowserRequest

    # For usageSummary()
    _what = _("page-component", "Page")

    def __init__(self,
                 required, name, permission,
                 factoryName=None, template=None, attribute=None,
                 layer='default'):

        # XXX A Interface comes out of the interface widget
        # wrapped on a proxy currently, which is not pickable
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

    def factories(self):

        self.validate()

        sm = zapi.getServiceManager(self)

        if self.factoryName:
            folder = self.__parent__.__parent__
            class_ = folder.resolve(self.factoryName)
        else:
            class_  = DefaultClass



        if self.attribute:
            return (AttrViewFactory(class_, self.attribute), )

        else:

            if self.template[0]=='/':
                # This is needed because we need to do an unrestricted zapi.
                # traverse
                root = zope.proxy.removeAllProxies(zapi.getRoot(sm))
                template = zapi.traverse(root, self.template)
            else:
                template = zapi.traverse(self.__parent__.__parent__,
                                         self.template)
            return (TemplateViewFactory(class_, template, self.permission), )

    factories = property(factories)


    def addNotify(self, event):
        "See IAddNotifiable"
        if self.template:
            template = zapi.traverse(self.__parent__.__parent__,self.template)
            dependents = IDependable(template)
            objectpath = zapi.getPath(self)
            dependents.addDependent(objectpath)
            # Also update usage, if supported
            adapter = IRegistered(template, None)
            if adapter is not None:
                adapter.addUsage(objectpath)


    def removeNotify(self, event):
        "See IRemoveNotifiable"
        super(PageRegistration, self).removeNotify(event)
        if self.template:
            template = zapi.traverse(self.__parent__.__parent__,self.template)
            dependents = IDependable(template)
            objectpath = zapi.getPath(self)
            dependents.removeDependent(objectpath)
            # Also update usage, if supported
            adapter = IRegistered(template, None)
            if adapter is not None:
                adapter.removeUsage(zapi.getPath(self))


class TemplateViewFactory:

    def __init__(self, cls, template, permission):
        self.cls, self.template, self.permission = cls, template, permission

    def __call__(self, object, request):
        checker = NamesChecker(__call__ = self.permission)
        template = BoundTemplate(self.template, self.cls(object, request))
        return ProxyFactory(template, checker)

class AttrViewFactory:

    def __init__(self, cls, attr):
        self.cls, self.attr = cls, attr

    def __call__(self, object, request):
        attr = getattr(self.cls(object, request), self.attr)
        return ProxyFactory(attr)

class DefaultClass:

    def __init__(self, context, request):
        self.context = context
        self.request = request

class BoundTemplate:

    def __init__(self, template, view):
        self.template = template
        self.view = view

    def __call__(self, template_usage=u'', *args, **kw):
        if not template_usage:
            kw["template_usage"] = template_usage
        return self.template.render(self.view, *args, **kw)

#BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB

from zope.app.event.function import Subscriber
import persistent
import sys
from zope.interface.adapter import ReadProperty

ViewRegistration.required    = ReadProperty(lambda self: self.forInterface)
ViewRegistration.factoryName = ReadProperty(lambda self: self.class_)
ViewRegistration.name        = ReadProperty(lambda self: self.viewName)

class ViewService(persistent.Persistent):
    pass

def fixup(event):
    # We delay this evil hackery until database open to prevent someone
    # successfully importing IBrowserPresentation through a normal import
    sys.modules['zope.app.services.view'] = sys.modules[__name__]
    IBrowserRequest = zope.publisher.interfaces.browser.IBrowserRequest
    zope.publisher.interfaces.browser.IBrowserPresentation = IBrowserRequest 
    
fixup = Subscriber(fixup)
