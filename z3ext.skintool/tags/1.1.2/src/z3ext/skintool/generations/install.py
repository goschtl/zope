##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""

$Id: install.py 3814 2008-11-14 10:40:03Z fafhrd91 $
"""
from zope import component
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import getSite, setSite
from zope.app.publication.zopepublication import ZopePublication

from z3ext.skintool import tool
from z3ext.skintool.interfaces import ISkinTool


def evolve(context):
    root = context.connection.root()[ZopePublication.root_name]

    def findObjectsProviding(root):
        if ISite.providedBy(root):
            yield root

        values = getattr(root, 'values', None)
        if callable(values):
            for subobj in values():
                for match in findObjectsProviding(subobj):
                    yield match

    for site in findObjectsProviding(root):
        setSite(site)

        skintool = component.getUtility(ISkinTool)
        layers = skintool.data.get('user_layers')

        if layers:
            skin = None
            ulayers = []
            for layer in layers:
                if layer in tool.skins_byname and skin is None:
                    skin = layer

                if layer in tool.layers_byname:
                    ulayers.append(layer)
                
            skintool.skin = skin
            skintool.layers = ulayers
