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


$Id: view.py,v 1.3 2002/12/21 19:58:26 stevea Exp $
"""
__metaclass__ = type

from Persistence import Persistent
from Persistence.PersistentDict import PersistentDict
from Zope.ComponentArchitecture.IViewService import IViewService
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.ComponentArchitecture import getServiceManager
from Zope.App.OFS.Services.ConfigurationInterfaces import IConfigurable
from Zope.App.OFS.Services.Configuration import ConfigurationRegistry
from Zope.App.OFS.Services.Configuration import SimpleConfiguration
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.ContextWrapper import ContextMethod
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty
from Zope.App.ComponentArchitecture.NextService import getNextService
from Zope.ComponentArchitecture import getSkin

from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.App.Traversing import getPhysicalRoot, traverse
from Zope.Exceptions import NotFoundError

from interfaces import IViewConfiguration, IPageConfiguration
from adapter import PersistentAdapterRegistry

class ViewService(Persistent):

    __implements__ = IViewService, IConfigurable

    def __init__(self):
        self._layers = PersistentDict()

    def queryConfigurationsFor(self, configuration, default=None):
        "See Zope.App.OFS.Services.ConfigurationInterfaces.IConfigurable"
        return self.queryConfigurations(
            configuration.viewName, configuration.layer,
            configuration.forInterface, configuration.presentationType,
            default)

    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(self, name, layer, 
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

    queryConfigurations = ContextMethod(queryConfigurations)
    
    def createConfigurationsFor(self, configuration):
        "See Zope.App.OFS.Services.ConfigurationInterfaces.IConfigurable"
        return self.createConfigurations(
            configuration.viewName, configuration.layer,            
            configuration.forInterface, configuration.presentationType)

    createConfigurationsFor = ContextMethod(createConfigurationsFor)

    def createConfigurations(self,
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
            registry = ConfigurationRegistry()
            adapter_registry.register(forInterface, presentationType, registry)

        return ContextWrapper(registry, self)

    createConfigurations = ContextMethod(createConfigurations)

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
        "See Zope.ComponentArchitecture.IViewService.IViewService"

        name = self.queryDefaultViewName(object, request)

        if name is None:
            raise NotFoundError, \
                  'No default view name found for object %s' % object

        return name

    getDefaultViewName = ContextMethod(getDefaultViewName)

    def queryDefaultViewName(self, object, request, default=None):
        "See Zope.ComponentArchitecture.IViewService.IViewService"

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

            for viewName in viewNames:
                registry = names_dict.get(viewName)

                if registry is None:
                    continue

                for match in registry.getRegisteredMatching(
                    required_interfaces,
                    presentation_type):
                    
                    result.append(match + (layer, viewName))
            
        return result

class ViewConfiguration(SimpleConfiguration):

    __implements__ = IViewConfiguration

    status = ConfigurationStatusProperty('Views')

    def __init__(self,
                 forInterface, viewName, presentationType,
                 factoryName, layer='default'):
        self.forInterface = forInterface
        self.presentationType = presentationType
        self.factoryName = factoryName
        self.viewName = viewName
        self.layer = layer

    def getView(self, object, request):
        sm = getServiceManager(self)
        factory = sm.resolve(self.factoryName)        
        return factory(object, request)

    getView = ContextMethod(getView)
    
class PageConfiguration(ViewConfiguration):

    __implements__ = IPageConfiguration
    
    def __init__(self,
                 forInterface, viewName, presentationType,
                 factoryName=None, template=None,
                 layer='default'):
        super(PageConfiguration, self).__init__(
            forInterface, viewName, presentationType,
            factoryName, layer)

        self.template = template

    def getView(self, object, request):
        sm = getServiceManager(self)

        if self.factoryName:
            factory = sm.resolve(self.factoryName)
        else:
            factory = DefaultFactory
        
        view = factory(object, request)

        # This is needed because we need to do an unrestricted traverse
        root = removeAllProxies(getPhysicalRoot(sm))
        
        template = traverse(root, self.template)

        return BoundTemplate(template, view)

    getView = ContextMethod(getView)


class DefaultFactory:

    def __init__(self, context, request):
        self.context = context
        self.request = request

class BoundTemplate:

    def __init__(self, template, view):
        self.template = template
        self.view = view

    def __call__(self, *args, **kw):
        return self.template.render(self.view, *args, **kw)

                 
