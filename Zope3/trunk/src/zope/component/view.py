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

$Id: view.py,v 1.6 2003/08/17 06:08:45 philikon Exp $
"""

from zope.interface.adapter import AdapterRegistry
from zope.interface import implements
from zope.component.exceptions import ComponentLookupError
from zope.component import getSkin
from zope.component.interfaces import IGlobalViewService
from zope.exceptions import NotFoundError

# XXX The GlobalViewService and LocalViewService contain a lot of
# duplicate code.  It may be good to refactor them so that the
# duplicate code is shared.  It would be non-trivial to design the
# shared code to allow the necessary customizations for the specific
# service.

class GlobalViewService:
    """The global view service.

    Internally, we use a data structure of the form:

    _layers: { layername -> layer }
    layer:  { viewname -> registry }
    registry: (required, pres_type) -> factory chain }
    """
    implements(IGlobalViewService)

    def __init__(self):
        self._layers = {}
        self._default_view_names = AdapterRegistry()

    def setDefaultViewName(self, i_required, i_provided, name):
        self._default_view_names.register(i_required, i_provided, name)

    def getView(self, object, name, request):
        '''See interface IViewService'''
        view = self.queryView(object, name, request)
        if view is None:
            type = request.getPresentationType()
            raise ComponentLookupError(object, name, type)
        return view

    def queryView(self, object, name, request, default=None):
        '''See interface IViewService'''

        type = request.getPresentationType()
        skin = request.getPresentationSkin()

        for layername in getSkin(object, skin, type):
            layer = self._layers.get(layername)
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

        views = self._layers.get(layer)
        if views is None:
            views = self._layers[layer] = {}

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
        name = self._default_view_names.getForObject(object, type)

        if name is None:
            name = default

        return name

    def getRegisteredMatching(self, required_interfaces=None,
                              presentation_type=None, viewName=None,
                              layer=None):
        # Return registration info matching keyword arg criteria.
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

    def all(self):
        return self._layers

    _clear = __init__

viewService = GlobalViewService()
provideView = viewService.provideView
setDefaultViewName = viewService.setDefaultViewName
_clear         = viewService._clear


# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
