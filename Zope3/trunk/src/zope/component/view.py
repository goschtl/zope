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

$Id: view.py,v 1.2 2002/12/25 14:13:31 jim Exp $
"""

from zope.interface.adapter import AdapterRegistry
from zope.component.exceptions import ComponentLookupError
from zope.component import getSkin
from zope.component.interfaces import IViewService
from zope.exceptions import NotFoundError

class IGlobalViewService(IViewService):

    def setDefaultViewName(i_required, i_provided, name):
        '''Add name to our registry of default view names for
           the interfaces given.
        '''

    def provideView(forInterface, name, type, factory, layer='default'):
        """Register a view factory

        The factory is a sequence. The last object in the sequence
        must be an IViewFactory. The other objects in the sequence
        must be adapter factories.
        """

class GlobalViewService:

    __implements__ = IGlobalViewService

    def __init__(self):
        self.__layers = {}
        self.__default_view_names = AdapterRegistry()

    def setDefaultViewName(self, i_required, i_provided, name):
        self.__default_view_names.register(i_required,
                                           i_provided,
                                           name)

    def getView(self, object, name, request):
        '''See interface IViewService'''
        view = self.queryView(object, name, request)
        if view is None:
            raise ComponentLookupError(object, name, type)
        return view

    def queryView(self, object, name, request, default=None):
        '''See interface IViewService'''

        type = request.getPresentationType()
        skin = request.getPresentationSkin()

        for layername in getSkin(object, skin, type):
            layer = self.__layers.get(layername)
            if not layer:
                continue

            reg = layer.get(name, None)
            if reg is None:
                continue

            makers = reg.getForObject(object, type)
            if not makers:
                continue

            result = object
            for maker in makers[:-1]:
                result = maker(result)

            return makers[-1](result, request)

        return default


    def provideView(self, forInterface, name, type, maker, layer='default'):
        '''See interface IGlobalViewService'''

        views = self.__layers.get(layer)
        if views is None:
            views = self.__layers[layer] = {}

        reg = views.get(name, None)
        if reg is None:
            reg = views[name] = AdapterRegistry()

        if not isinstance(maker, (list, tuple)):
            maker = [maker]
        else:
            maker = list(maker)

        if not maker == filter(callable, maker):
            raise TypeError("The registered component callable is not "
                            "callable")

        reg.register(forInterface, type, maker)

    def getDefaultViewName(self, object, request):
        '''See interface IViewService'''

        name = self.queryDefaultViewName(object, request)

        if name is None:
            raise NotFoundError, \
                  'No default view name found for object %s' % object

        return name

    def queryDefaultViewName(self, object, request, default=None):
        '''See interface IViewService'''

        type = request.getPresentationType()
        name = self.__default_view_names.getForObject(object, type)

        if name is None:
            name = default

        return name

    def all(self):
        return self.__layers

    _clear = __init__

viewService = GlobalViewService()
provideView = viewService.provideView
setDefaultViewName = viewService.setDefaultViewName
_clear         = viewService._clear


# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
