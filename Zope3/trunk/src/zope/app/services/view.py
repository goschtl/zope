##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""View Service
$Id: view.py,v 1.28 2003/06/24 15:38:04 jeremy Exp $
"""
__metaclass__ = type

from __future__ import generators

from persistence import Persistent
from persistence.dict import PersistentDict

from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.component.interfaces import IViewService, IGlobalViewService
from zope.component.exceptions import ComponentLookupError

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.services.interface import IInterfaceBasedRegistry
from zope.app.interfaces.services.registration \
     import IRegistry, IRegistration, ActiveStatus
from zope.app.services.registration import RegistrationStack
from zope.app.services.registration import SimpleRegistration
from zope.app.services.servicenames import Views
from zope.app.component.nextservice import getNextService
from zope.app import zapi
from zope.interface import implements

from zope.security.checker import NamesChecker, ProxyFactory

from zope.proxy import removeAllProxies
from zope.exceptions import NotFoundError

from zope.app.interfaces.services.interface import IInterfaceBasedRegistry
from zope.app.interfaces.services.view import IViewRegistration
from zope.app.interfaces.services.view import IPageRegistration
from zope.app.interfaces.services.view import ILocalViewService
from zope.app.services.adapter import PersistentAdapterRegistry
from zope.configuration.exceptions import ConfigurationError
from zope.app.interfaces.services.service import ISimpleService

class ViewService(Persistent):

    implements(IViewService, ILocalViewService, IRegistry, ISimpleService,
               IInterfaceBasedRegistry)

    def __init__(self):
        self._layers = PersistentDict()

    # All the methods defined here are context methods
    zapi.ContextAwareDescriptors()

    def queryRegistrationsFor(self, registration, default=None):
        "See IRegistry"
        return self.queryRegistrations(
            registration.viewName, registration.layer,
            registration.forInterface, registration.presentationType,
            default)

    def queryRegistrations(self, name, layer,
                            forInterface, presentationType, default=None):

        names = self._layers.get(layer)
        if names is None:
            return default

        adapter_registry = names.get(name)
        if adapter_registry is None:
            return default

        registry = adapter_registry.getRegistered(
            forInterface, presentationType)

        if registry is None:
            return default

        return zapi.ContextWrapper(registry, self)

    def createRegistrationsFor(self, registration):
        "See IRegistry"
        return self.createRegistrations(
            registration.viewName, registration.layer,
            registration.forInterface, registration.presentationType)

    def createRegistrations(self,
                             viewName, layer, forInterface, presentationType):

        names = self._layers.get(layer)
        if names is None:
            names = PersistentDict()
            self._layers[layer] = names

        adapter_registry = names.get(viewName)
        if adapter_registry is None:
            adapter_registry = PersistentAdapterRegistry()
            names[viewName] = adapter_registry

        registry = adapter_registry.getRegistered(
            forInterface, presentationType)

        if registry is None:
            registry = RegistrationStack()
            adapter_registry.register(forInterface, presentationType, registry)

        return zapi.ContextWrapper(registry, self)

    def getView(self, object, name, request):
        view = self.queryView(object, name, request)
        if view is None:
            raise ComponentLookupError(object, name)
        return view

    def queryView(self, object, name, request, default=None):

        type = request.getPresentationType()
        skin = request.getPresentationSkin()

        for layername in zapi.getSkin(object, skin, type):
            layer = self._layers.get(layername)
            if not layer:
                continue

            reg = layer.get(name, None)
            if reg is None:
                continue

            registry = reg.getForObject(
                object, type,
                filter = lambda registry:
                         zapi.ContextWrapper(registry, self).active(),
                )

            if registry is None:
                continue

            registry = zapi.ContextWrapper(registry, self)
            view = registry.active().getView(object, request)
            return view

        views = getNextService(self, Views)

        return views.queryView(object, name, request, default)

    def getDefaultViewName(self, object, request):
        "See IViewService"

        name = self.queryDefaultViewName(object, request)

        if name is None:
            raise NotFoundError(
                "No default view name found for object %s" % object)

        return name

    def queryDefaultViewName(self, object, request, default=None):
        "See IViewService"

        # XXX: need to do our own defaults as well.
        views = getNextService(self, Views)
        return views.queryDefaultViewName(object, request, default)

    def getRegisteredMatching(self, required_interfaces=None,
                              presentation_type=None, viewName=None,
                              layer=None):
        if layer is None:
            layers = self._layers.keys()
        else:
            layers = (layer, )

        result = []

        for layer in layers:
            names_dict = self._layers.get(layer)
            if names_dict is None:
                continue

            if viewName is None:
                viewNames = names_dict.keys()
            else:
                viewNames = (viewName, )

            for vn in viewNames:
                registry = names_dict.get(vn)
                if registry is None:
                    continue

                for match in registry.getRegisteredMatching(
                    required_interfaces,
                    presentation_type):

                    result.append(match + (layer, vn))

        return result

    def getRegistrationsForInterface(self, iface):
        for t in self.getRegisteredMatching(required_interfaces=[iface]):
            # XXX getRegisteredMatching ought to return a wrapped object
            reg = zapi.ContextWrapper(t[2], self) # t[2] is registration stack
            for info in reg.info():
                yield info["registration"]

        next = getNextService(self, Views)
        next = zapi.queryAdapter(next, IInterfaceBasedRegistry)
        if next is None:
            return
        for r in next.getRegistrationsForInterface(iface):
            yield r

class RegistrationAdapter:
    """Adapter to create registrations from factory chains."""

    implements(IInterfaceBasedRegistry)
    __used_for__ = IGlobalViewService

    def __init__(self, gvs):
        self.gvs = gvs

    def getRegistrationsForInterface(self, iface):
        for t in self.gvs.getRegisteredMatching(required_interfaces=[iface]):
            yield GlobalViewRegistration(*t)
            
class GlobalViewRegistration:
    """Registrations representing global view service thingies."""

    implements(IRegistration)

    serviceType = Views
    status = ActiveStatus

    def __init__(self, req, ptype, factories, layer, viewName):
        self.forInterface = req
        self.ptype = ptype
        self.factories = factories
        self.layer = layer
        self.viewName = viewName

    def usageSummary(self):
        if self.forInterface is None:
            ifname = _("(Anything)")
        else:
            ifname = self.forInterface.__name__
        L = [self.viewName, self.ptype.__name__, _("View"), _("for"), ifname]
        if self.layer and self.layer != "default":
            L.extend([_("in layer"), self.layer])
        return " ".join(L)

    def implementationSummary(self):
        # XXX This should report the ZCML that it came from.
        return _("Registered by ZCML")

class ViewRegistration(SimpleRegistration):

    implements(IViewRegistration)

    serviceType = Views

    _what = _("View") # For usageSummary(); subclass may override

    def __init__(self,
                 forInterface, viewName, presentationType,
                 class_, permission, layer='default'):
        self.forInterface = forInterface
        self.presentationType = presentationType
        self.class_ = class_
        self.viewName = viewName
        self.layer = layer
        self.permission = permission

    def getView(self, object, request):
        sm = zapi.getServiceManager(self)
        factory = sm.resolve(self.class_)
        return factory(object, request)

    getView = zapi.ContextMethod(getView)

    def usageSummary(self):
        if self.forInterface is None:
            ifname = _("(Anything)")
        else:
            ifname = self.forInterface.__name__
        pname = self.presentationType.__name__
        L = [self.viewName, _("for"), pname, self._what, ifname]
        if self.layer and self.layer != "default":
            L.extend([_("in layer"), self.layer])
        return " ".join(L)
    
class PageRegistration(ViewRegistration):

    implements(IPageRegistration)

    # We only care about browser pages
    presentationType = IBrowserPresentation

    _what = _("Page") # For usageSummary()

    def __init__(self,
                 forInterface, viewName, permission,
                 class_=None, template=None, attribute=None,
                 layer='default'):

        super(PageRegistration, self).__init__(
            forInterface, viewName, self.presentationType,
            class_, permission, layer)

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
        if self.class_:
            L.append("class=%s" % self.class_)
        if self.attribute:
            L.append("attribute=%s" % self.attribute)
        return ", ".join(L)

    def validate(self):
        if self.template and self.attribute:
            raise ConfigurationError(
                "PageRegistration for %s view name %s: "
                "Cannot have both 'template' and 'attribute' at the same time." %
                (self.forInterface, self.viewName))

        if not self.template and not self.attribute:
            raise ConfigurationError(
                "PageRegistration for %s view name %s: "
                "Should have a 'template' or 'attribute' attribute." %
                (self.forInterface, self.viewName))

        if not self.class_ and self.attribute:
            raise ConfigurationError(
                "PageRegistration for %s view name %s: "
                "Cannot have an 'attribute' without a 'class_'." %
                (self.forInterface, self.viewName))

    def getView(self, object, request):


        self.validate()

        sm = zapi.getServiceManager(self)

        if self.class_:
            class_ = sm.resolve(self.class_)
            class_ = type(class_.__name__, (class_, DefaultClass), {})
        else:
            class_  = DefaultClass

        view = class_(object, request)

        # This is needed because we need to do an unrestricted zapi.traverse
        root = removeAllProxies(zapi.getRoot(sm))

        if self.attribute:
            template = getattr(view, self.attribute)
        else:
            template = zapi.traverse(root, self.template)
            template = BoundTemplate(template, view)

        checker = NamesChecker(__call__ = self.permission)

        return ProxyFactory(template, checker)

    getView = zapi.ContextMethod(getView)

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


# XXX Pickle backward compatability
PageConfiguration = PageRegistration
ViewConfiguration = ViewRegistration
