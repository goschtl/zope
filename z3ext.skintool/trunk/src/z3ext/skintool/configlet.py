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

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
from zope import event
from zope.component import getUtility
from zope.lifecycleevent import ObjectModifiedEvent

from z3ext.skintool import tool
from z3ext.skintool.interfaces import _, ISkinTool
from z3ext.statusmessage.interfaces import IStatusMessage


class SkintoolEditForm(object):

    def listSkins(self):
        skins = []
        for skin, name, title, description, require \
                in tool.skins_registry.values():
            skins.append((title, name, 
                          {'name': name,
                           'title': title,
                           'selected': self.tool.skin == name,
                           'description': description}))
        skins.sort()

        skins.insert(0, ('', '', 
                         {'name': '__no__',
                          'title': _(u'No skin'),
                          'selected': self.tool.skin == None,
                          'description': u''}))
        return [info for t, n, info in skins]
    
    def listLayers(self):
        layers = []
        for layer, name, title, description in tool.layers_registry.values():
            layers.append((title, name, 
                           {'name': name,
                            'title': title,
                            'selected': name in self.tool.layers,
                            'description': description}))
        layers.sort()

        return [info for t, n, info in layers]

    def update(self):
        self.tool = getUtility(ISkinTool)

        if 'form.buttons.save' in self.request:
            skin = self.request.get('skin', '__no__')
            if skin == '__no__':
                self.tool.skin = None
            else:
                self.tool.skin = skin

            self.tool.layers = self.request.get('layers', [])
            event.notify(ObjectModifiedEvent(self.tool))
            IStatusMessage(self.request).add(_(u'Changes has been saved.'))
