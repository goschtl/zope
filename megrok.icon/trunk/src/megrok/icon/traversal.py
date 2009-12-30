# -*- coding: utf-8 -*-

import grokcore.component as grok

from megrok.icon import IIconRegistry
from zope.component import queryUtility
from zope.interface import Interface
from zope.location.interfaces import ILocation
from zope.location.location import locate, LocationProxy
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.publisher.interfaces.http import IHTTPRequest
from zope.security.proxy import removeSecurityProxy
from zope.site.hooks import getSite
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.interfaces import ITraversable, TraversalError


class IconTraverser(grok.MultiAdapter):
    grok.name('icon')
    grok.provides(ITraversable)
    grok.adapts(Interface, IHTTPRequest)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, icon=[]):
        if not name:
            raise TraversalError('Icon registry name is missing.')
        registry = queryUtility(IIconRegistry, name=name)
        if registry is not None:
            return registry
        raise NotFound(self.context, name, self.request)


class IconRegistryTraverser(grok.MultiAdapter):
    grok.provides(IPublishTraverse)
    grok.adapts(IIconRegistry, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def publishTraverse(self, request, name):
        registry = removeSecurityProxy(self.context)
        icon = registry.resource(name)
        if icon is not None:
            return removeSecurityProxy(icon(self.request))
        raise NotFound(self.context, name, request)


@grok.adapter(IIconRegistry)
@grok.implementer(ILocation)
def locate_registry(registry):
    site = getSite()
    name = '++icon++' + grok.name.bind().get(registry)
    locatable = LocationProxy(registry)
    locate(locatable, site, name=name)
    return locatable
