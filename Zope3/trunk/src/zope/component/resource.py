##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: resource.py,v 1.2 2002/12/25 14:13:31 jim Exp $
"""

from zope.interface.implementor import ImplementorRegistry
from zope.component.exceptions import ComponentLookupError
from zope.component import getSkin
from zope.component.interfaces import IResourceService

class IGlobalResourceService(IResourceService):

    def provideResource(name, type, factory, layer='default'):
        """Provide a resource

        A resource is an inependent component that provides a view
        type.  It is like a view except that it acts by itself,
        typically to support views. Common resources include images,
        style sheets, etc.

        Arguments:

        name -- The resource name

        type -- The resource type, expressed as an interface

        factory -- an IResourceFactory that computes a resource.

        layer -- Optional skin layer. Layers are used to define skins.
        """

class GlobalResourceService:

    def __init__(self):
        self.__layers = {}

    __implements__ = IGlobalResourceService

    def getResource(self, object, name, request):
        '''See interface IResourceService'''

        resource = self.queryResource(object, name, request)

        if resource is None:
            raise ComponentLookupError(object, name, type)

        return resource

    def queryResource(self, object, name, request, default=None):
        '''See interface IResourceService'''

        type = request.getPresentationType()
        skin = request.getPresentationSkin()

        for layername in getSkin(object, skin, type):
            layer = self.__layers.get(layername)
            if not layer: continue
            reg = layer.get(name, None)
            if reg is None: continue
            factory = reg.get(type)
            if factory is None:
                continue

            return factory(request)

        return default


    def provideResource(self, name, type, factory, layer='default'):
        '''See interface IGlobalResourceService'''

        resources = self.__layers.get(layer)
        if resources is None:
            resources = self.__layers[layer] = {}

        reg = resources.get(name, None)
        if reg is None:
            reg = resources[name] = ImplementorRegistry()

        reg.register(type, factory)

    _clear = __init__

resourceService = GlobalResourceService()
provideResource = resourceService.provideResource
_clear             = resourceService._clear


# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
