##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests for catalog

Note that indexes &c already have test suites, we only have to check that
a catalog passes on events that it receives.

$Id$
"""
import unittest
import doctest

from zope.interface import implements
from zope.app.index.interfaces.field import IUIFieldCatalogIndex
from zope.app.event.interfaces import ISubscriber
from zope.app.hub.interfaces import IObjectHub
from zope.app.catalog.interfaces.index import ICatalogIndex
from zope.index.interfaces import ISimpleQuery
from zope.app.site.interfaces import ISite
from zope.app import zapi

from zope.app.catalog.catalog import Catalog
from zope.app.catalog.catalog import CatalogBaseAddSubscriber
from zope.app.catalog.catalog import CatalogBaseRemoveSubscriber
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getGlobalServices
from zope.app.servicenames import HubIds
from BTrees.IIBTree import IISet

from zope.app.index.tests.test_objectretrievingprocessor import FakeObjectHub

import zope.app.hub as Hub

regEvt = Hub.ObjectRegisteredHubEvent
unregEvt = Hub.ObjectUnregisteredHubEvent
modEvt = Hub.ObjectModifiedHubEvent

class CFakeObjectHub(FakeObjectHub):
    def iterObjectRegistrations(self):
        def gen(things):
            for hubid, obj in things:
                loc = "/%s"%hubid
                yield loc,hubid,obj
        return gen(self.data.items())


class StubIndex(object):
    implements(ISimpleQuery, ISubscriber, ICatalogIndex, IUIFieldCatalogIndex)

    def __init__(self, field_name, interface=None):
        self._field_name = field_name
        self.interface = interface
        self._notifies = []

    def notify(self, event):
        self._notifies.append(event)

    def clear(self):
        self._notifies = []

    def _getterms(self):
        d = {}
        for e in self._notifies:
            ob = e.object
            term = getattr(e.object ,self._field_name, '')
            d.setdefault(term, []).append(e.hubid)
        return d

    def query(self, term, start=0, count=None):
        termdict = self._getterms()
        res = termdict.get(term, [])
        return IISet(res)

class stoopid(object):
    def __init__(self, **kw):
        self.__dict__ = kw

class DummyCatalog:

    def __init__(self):
        self.subscribed = False

    def subscribeEvents(self, update=False):
        self.subscribed = True
        
    def getSubscribed(self):
        return self.subscribed

    def unsubscribeEvents(self):
        self.subscribed = False
        
class TestEventAdapters:
    def test_addNotify(self):
        """
        First we create a dummy catalog and an adapter for it.
        
        >>> catalog = DummyCatalog()
        >>> adapter = CatalogBaseAddSubscriber(catalog, None)

        Now call notification
        >>> adapter.notify(None)

        Check to make sure the adapter added the path
        >>> catalog.getSubscribed()
        True
        """
    
    def test_deleteNotify(self):
        """
        First we create a dummy catalog and an adapter for it.
        
        >>> catalog = DummyCatalog()
        >>> adapter = CatalogBaseAddSubscriber(catalog, None)

        Now call notification
        >>> adapter.notify(None)

        Check to make sure the adapter subscribed
        >>> catalog.getSubscribed()
        True

        Now create a removal adapter and notify it
        >>> adapter = CatalogBaseRemoveSubscriber(catalog, None)
        >>> adapter.notify(None)

        Check to make sure the adapter unsubscribed
        >>> catalog.getSubscribed()
        False
        """

class Test(PlacelessSetup, unittest.TestCase):

    def test_catalog_add_del_indexes(self):
        catalog = Catalog()
        index = StubIndex('author', None)
        catalog['author'] = index
        self.assertEqual(catalog.keys(), ['author'])
        index = StubIndex('title', None)
        catalog['title'] = index
        indexes = catalog.keys()
        indexes.sort()
        self.assertEqual(indexes, ['author', 'title'])
        del catalog['author']
        self.assertEqual(catalog.keys(), ['title'])

    def test_catalog_notification_passing(self):
        catalog = Catalog()
        catalog['author'] = StubIndex('author', None)
        catalog['title'] = StubIndex('title', None)
        catalog.notify(regEvt(None, None, 'reg1', 1))
        catalog.notify(regEvt(None, None, 'reg2', 2))
        catalog.notify(regEvt(None, None, 'reg3', 3))
        catalog.notify(unregEvt(None, None, 'unreg4', 4))
        catalog.notify(unregEvt(None, None, 'unreg5', 5))
        catalog.notify(modEvt(None, None, 'mod6', 6))
        for index in catalog.values():
            checkNotifies = index._notifies
            self.assertEqual(len(checkNotifies), 6)
            notifLocs = [ x.location for x in checkNotifies ]
            self.assertEqual(notifLocs, ['reg1', 'reg2', 'reg3', 
                                         'unreg4', 'unreg5','mod6' ])
            self.assertEqual(notifLocs, ['reg1', 'reg2', 'reg3', 
                                         'unreg4', 'unreg5','mod6' ])
        catalog.clearIndexes()
        for index in catalog.values():
            checkNotifies = index._notifies
            self.assertEqual(len(checkNotifies), 0)

    def _frob_objecthub(self, ints=1, apes=1):
        hub = CFakeObjectHub()
        service_manager = getGlobalServices()
        service_manager.defineService(HubIds, IObjectHub)
        service_manager.provideService(HubIds, hub)
        # whack some objects in our little objecthub
        if ints:
            for i in range(10):
                hub.register("<object %s>"%i)
        if apes:
            hub.register(stoopid(simiantype='monkey', name='bobo'))
            hub.register(stoopid(simiantype='monkey', name='bubbles'))
            hub.register(stoopid(simiantype='monkey', name='ginger'))
            hub.register(stoopid(simiantype='bonobo', name='ziczac'))
            hub.register(stoopid(simiantype='bonobo', name='bobo'))
            hub.register(stoopid(simiantype='punyhuman', name='anthony'))
            hub.register(stoopid(simiantype='punyhuman', name='andy'))
            hub.register(stoopid(simiantype='punyhuman', name='kev'))

    def test_updateindexes(self):
        "test a full refresh"
        self._frob_objecthub()
        catalog = Catalog()
        catalog['author'] = StubIndex('author', None)
        catalog['title'] = StubIndex('author', None)
        catalog.updateIndexes()
        for index in catalog.values():
            checkNotifies = index._notifies
            self.assertEqual(len(checkNotifies), 18)
            notifLocs = [ x.location for x in checkNotifies ]
            notifLocs.sort()
            expected = [ "/%s"%(i+1) for i in range(18) ]
            expected.sort()
            self.assertEqual(notifLocs, expected)

    def test_basicsearch(self):
        "test the simple searchresults interface"
        self._frob_objecthub(ints=0)
        catalog = Catalog()
        catalog['simiantype'] = StubIndex('simiantype', None)
        catalog['name'] = StubIndex('name', None)
        catalog.updateIndexes()
        res = catalog.searchResults(simiantype='monkey')
        names = [ x.name for x in res ]
        names.sort()
        self.assertEqual(len(names), 3)
        self.assertEqual(names, ['bobo', 'bubbles', 'ginger'])
        res = catalog.searchResults(name='bobo')
        names = [ x.simiantype for x in res ]
        names.sort()
        self.assertEqual(len(names), 2)
        self.assertEqual(names, ['bonobo', 'monkey'])
        res = catalog.searchResults(simiantype='punyhuman', name='anthony')
        self.assertEqual(len(res), 1)
        ob = iter(res).next()
        self.assertEqual((ob.name,ob.simiantype), ('anthony', 'punyhuman'))
        res = catalog.searchResults(simiantype='ape', name='bobo')
        self.assertEqual(len(res), 0)
        res = catalog.searchResults(simiantype='ape', name='mwumi')
        self.assertEqual(len(res), 0)
        self.assertRaises(ValueError, catalog.searchResults, 
                            simiantype='monkey', hat='beret')
        res = list(res)

def test_suite():
    import sys
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        doctest.DocTestSuite(sys.modules[__name__]),
        ))

if __name__ == "__main__":
    unittest.main()

