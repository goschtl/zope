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

$Id$
"""
from zope import event
from zope.app.component.interfaces import ISite
from zope.app.generations.utility import findObjectsProviding
from zope.app.publication.zopepublication import ZopePublication
from zope.lifecycleevent import ObjectCreatedEvent
from z3ext.controlpanel.storage import ConfigletData, ConfigletDataStorage


def evolve(context):
    root = context.connection.root()[ZopePublication.root_name]

    for site in findObjectsProviding(root, ISite):
        ann = getattr(site, '__annotations__', None)
        if ann is None:
            continue

        data = ann.get('z3ext.controlpanel.Settings')
        if data is None:
            continue

        sm = site.getSiteManager()

        storage = ConfigletDataStorage()
        event.notify(ObjectCreatedEvent(storage))

        if 'controlpanel' in sm:
            del sm['controlpanel']

        sm['controlpanel'] = storage

        for name, cdata in data.items():
            configlet = ConfigletData()
            event.notify(ObjectCreatedEvent(storage))
            storage[name] = configlet

            for n, v in cdata.items():
                if hasattr(v, '_p_jar'):
                    if storage._p_jar is not v._p_jar:
                        v = copy(v)

                configlet[n] = v

        del ann['z3ext.controlpanel.Settings']
