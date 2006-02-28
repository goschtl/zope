##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Persistent component managers

$Id$
"""
import persistent.mapping
import persistent.list
import zope.interface.adapter

import zope.component.components

class PersistentAdapterRegistry(zope.interface.adapter.AdapterRegistry,
                                persistent.Persistent):

    def changed(self):
        self._p_changed = True
        super(PersistentAdapterRegistry, self).changed()
        
class PersistentComponents(zope.component.components.Components):

    def _init_registries(self):
        self.adapters = PersistentAdapterRegistry()
        self.utilities = PersistentAdapterRegistry()

    def _init_registrations(self):
        self._utility_registrations = persistent.mapping.PersistentMapping()
        self._adapter_registrations = persistent.mapping.PersistentMapping()
        self._subscription_registrations = persistent.list.PersistentList()
        self._handler_registrations = persistent.list.PersistentList()

    
