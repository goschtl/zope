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
$Id: view.py,v 1.24 2003/06/21 21:22:12 jim Exp $
"""
__metaclass__ = type

from persistence import Persistent
from persistence.dict import PersistentDict

from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.component.interfaces import IViewService
from zope.component.exceptions import ComponentLookupError
from zope.component import getServiceManager
from zope.app.interfaces.services.registration import IRegistry
from zope.app.services.registration import RegistrationStack
from zope.app.services.registration import SimpleRegistration
from zope.app.context import ContextWrapper
from zope.context import ContextMethod
from zope.app.services.registration import RegistrationStatusProperty
from zope.app.component.nextservice import getNextService
from zope.component import getSkin
from zope.interface import implements

from zope.security.checker import NamesChecker, ProxyFactory

from zope.proxy import removeAllProxies
from zope.app.traversing import getRoot, traverse
from zope.exceptions import NotFoundError

from zope.app.interfaces.services.view import IViewRegistration
from zope.app.interfaces.services.view import IPageRegistration
from zope.app.services.adapter import PersistentAdapterRegistry
from zope.configuration.exceptions import ConfigurationError
from zope.app.interfaces.services.service import ISimpleService

class ViewService(Persistent):

    implements(IViewService, IRegistry, ISimpleService)

    def __init__(self):
        self._layers = PersistentDict()

    def queryRegistrationsFor(self, registration, default=None):
        "See IRegistry"
        return self.queryRegistrations(
            registration.viewName, registration.layer,
            registration.forInterface, registration.presentationType,
            default)

    queryRegistrationsFor = ContextMethod(queryRegistrationsFor)

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

        return ContextWrapper(registry, self)

    queryRegistrations = ContextMethod(queryRegistrations)

    def createRegistrationsFor(self, registration):
        "See IRegistry"
        return self.createRegistrations(
            registration.viewName, registration.layer,
            registration.forInterface, registration.presentationType)

    createRegistrationsFor = ContextMethod(createRegistrationsFor)

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

        return ContextWrapper(registry, self)

    createRegistrations = ContextMethod(createRegistrations)

    def getView(self, object, name, request):
        view = self.queryView(object, name, request)
        if view is None:
            raise ComponentLookupError(object, name)
        return view

    getView = ContextMethod(getView)

    def queryView(self, object, name, request, default=None):

        type = request.getPresentationType()
        skin = request.getPresentationSkin()

        for layername in getSkin(object, skin, type):
            layer = self._layers.get(layername)
            if not layer:
                continue

            reg = layer.get(name, None)
            if reg is None:
                continue

            registry = reg.getForObject(
                object, type,
                filter = lambda registry:
                         ContextWrapper(registry, self).active(),
                )

            if registry is None:
                continue

            registry = ContextWrapper(registry, self)
            view = registry.active().getView(object, request)
            return view

        views = getNextService(self, 'Views')

        return views.queryView(object, name, request, default)

    queryView = ContextMethod(queryView)

    def getDefaultViewName(self, object, request):
        "See IViewService"

        name = self.queryDefaultViewName(object, request)

        if name is None:
            raise NotFoundError, \
                  'No default view name found for object %s' % object

        return name

    getDefaultViewName = ContextMethod(getDefaultViewName)

    def queryDefaultViewName(self, object, request, default=None):
        "See IViewService"

        # XXX: need to do our own defaults as well.
        views = getNextService(self, 'Views')
        return views.queryDefaultViewName(object, request, default)

    queryDefaultViewName = ContextMethod(queryDefaultViewName)

    def getRegisteredMatching(self,
                              required_interfaces=None,
                              presentation_type=None,
                              viewName=None,
                              layer=None,
                              ):
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

class ViewRegistration(SimpleRegistration):

    implements(IViewRegistration)

    serviceType = 'Views'

    status = RegistrationStatusProperty()

    _what = "View" # For usageSummary(); subclass may override

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
        sm = getServiceManager(self)
        factory = sm.resolve(self.class_)
        return factory(object, request)

    getView = ContextMethod(getView)

    def usageSummary(self):
        # XXX L10N This should be localizable.
        ifname = getattr(self.forInterface, '__name__', "(Anything)")
        s = "%s %s for %s" % (self.viewName, self._what, ifname)
        if self.layer and self.layer != "default":
            s = "%s in layer %s" % (s, self.layer)
        return s

class PageRegistration(ViewRegistration):

    implements(IPageRegistration)

    # We only care about browser pages
    presentationType = IBrowserPresentation

    _what = "Page" # For usageSummary()

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

        sm = getServiceManager(self)

        if self.class_:
            class_ = sm.resolve(self.class_)
            class_ = type(class_.__name__, (class_, DefaultClass), {})
        else:
            class_  = DefaultClass

        view = class_(object, request)

        # This is needed because we need to do an unrestricted traverse
        root = removeAllProxies(getRoot(sm))

        if self.attribute:
            template = getattr(view, self.attribute)
        else:
            template = traverse(root, self.template)
            template = BoundTemplate(template, view)

        checker = NamesChecker(__call__ = self.permission)

        return ProxyFactory(template, checker)

    getView = ContextMethod(getView)

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
