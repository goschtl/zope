##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" skintool implementation

$Id$
"""
from zope import interface, component
from zope.component import getSiteManager, getAdapters, getUtilitiesFor
from zope.security.proxy import removeSecurityProxy
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.publisher.interfaces.browser import \
     IDefaultSkin, IBrowserRequest, IDefaultBrowserLayer
from zope.app.component.hooks import getSite

from interfaces import IDefaultLayer, IDefaultLayers, ISkinTool

layers_byname = {}
layers_registry = {}


class SkinTool(object):
    interface.implements(ISkinTool)

    def generate(self):
        layers = tuple(self.user_layers)

        bases = self._get_default()

        for name in layers:
            layer = layers_byname.get(name)
            if layer is not None:
                self._get_layers(layer, bases)

        # get base skin
        adapters = getSiteManager().adapters
        skin = adapters.lookup((IBrowserRequest,), IDefaultSkin, name='')
        if skin is not None:
            bases.insert(0, skin)
        else:
            bases.insert(0, IDefaultBrowserLayer)

        bases.reverse()
        return bases

    def _get_default(self):
        layers = []
        for name, adapter in getAdapters((getSite(),), IDefaultLayers):
            for layer in adapter.layers:
                self._get_layers(layer, layers)

        for name, layer in getUtilitiesFor(IDefaultLayer):
            self._get_layers(layer, layers)

        return layers

    def _get_layers(self, layer, layers):
        if layer in layers:
            return

        info = layers_registry.get(layer)

        if info is not None:
            for l in info[4]:
                self._get_layers(l, layers)

        layers.append(layer)


@component.adapter(ISkinTool, IObjectModifiedEvent)
def skinToolModified(*args):
    try:
        del removeSecurityProxy(getSite())._v_skin
    except:
        pass
