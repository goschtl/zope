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
from zope.interface.verify import verifyObject
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup
from BTrees.IIBTree import IISet
from zope.app.uniqueid.interfaces import IUniqueIdUtility

from zope.index.interfaces import IInjection, ISimpleQuery
from zope.app.catalog.interfaces import ICatalog
from zope.app.catalog.catalog import Catalog


class ReferenceStub:
    def __init__(self, obj):
        self.obj = obj

    def __call__(self):
        return self.obj


class UniqueIdUtilityStub:
    """A stub for UniqueIdUtility."""
    implements(IUniqueIdUtility)

    def __init__(self):
        self.ids = {}
        self.objs = {}
        self.lastid = 0

    def _generateId(self):
        self.lastid += 1
        return self.lastid

    def register(self, ob):
        if ob not in self.ids:
            uid = self._generateId()
            self.ids[ob] = uid
            self.objs[uid] = ob
        else:
            return self.ids[ob]

    def unregister(self, ob):
        uid = self.ids[ob]
        del self.ids[ob]
        del self.objs[id]

    def getObject(self, uid):
        return self.objs[uid]

    def getId(self, ob):
        return self.ids[ob]

    def items(self):
        return [(id, ReferenceStub(obj)) for id, obj in self.objs.items()]


class StubIndex:
    """A stub for Index."""

    implements(ISimpleQuery, IInjection)

    def __init__(self, field_name, interface=None):
        self._field_name = field_name
        self.interface = interface
        self.doc = {}

    def index_doc(self, docid, obj):
        self.doc[docid] = obj

    def unindex_doc(self, docid):
        del self.doc[docid]

    def query(self, term, start=0, count=None):
        results = []
        for docid in self.doc:
            obj = self.doc[docid]
            fieldname = getattr(obj, self._field_name, '')
            if fieldname == term:
                results.append(docid)
        return IISet(results)


class stoopid:
    def __init__(self, **kw):
        self.__dict__ = kw


class Test(PlacelessSetup, unittest.TestCase):

    def test_catalog_add_del_indexes(self):
        catalog = Catalog()
        verifyObject(ICatalog, catalog)
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

    def _frob_uniqueidutil(self, ints=True, apes=True):
        uidutil = UniqueIdUtilityStub()
        ztapi.provideUtility(IUniqueIdUtility, uidutil)
        # whack some objects in our little objecthub
        if ints:
            for i in range(10):
                uidutil.register("<object %s>"%i)
        if apes:
            uidutil.register(stoopid(simiantype='monkey', name='bobo'))
            uidutil.register(stoopid(simiantype='monkey', name='bubbles'))
            uidutil.register(stoopid(simiantype='monkey', name='ginger'))
            uidutil.register(stoopid(simiantype='bonobo', name='ziczac'))
            uidutil.register(stoopid(simiantype='bonobo', name='bobo'))
            uidutil.register(stoopid(simiantype='punyhuman', name='anthony'))
            uidutil.register(stoopid(simiantype='punyhuman', name='andy'))
            uidutil.register(stoopid(simiantype='punyhuman', name='kev'))

    def test_updateindexes(self):
        """Test a full refresh."""
        self._frob_uniqueidutil()
        catalog = Catalog()
        catalog['author'] = StubIndex('author', None)
        catalog['title'] = StubIndex('author', None)
        catalog.updateIndexes()
        for index in catalog.values():
            checkNotifies = index.doc
            self.assertEqual(len(checkNotifies), 18)
            ### notifLocs = [ x.location for x in checkNotifies ]
            ### notifLocs.sort()
            ### expected = [ "/%s"%(i+1) for i in range(18) ]
            ### expected.sort()
            ### self.assertEqual(notifLocs, expected)

    def test_basicsearch(self):
        """Test the simple search results interface."""
        self._frob_uniqueidutil(ints=0)
        catalog = Catalog()
        catalog['simiantype'] = StubIndex('simiantype', None)
        catalog['name'] = StubIndex('name', None)
        catalog.updateIndexes()

        res = catalog.searchResults(simiantype='monkey')
        names = [x.name for x in res]
        names.sort()
        self.assertEqual(len(names), 3)
        self.assertEqual(names, ['bobo', 'bubbles', 'ginger'])

        res = catalog.searchResults(name='bobo')
        names = [x.simiantype for x in res]
        names.sort()
        self.assertEqual(len(names), 2)
        self.assertEqual(names, ['bonobo', 'monkey'])

        res = catalog.searchResults(simiantype='punyhuman', name='anthony')
        self.assertEqual(len(res), 1)
        ob = iter(res).next()
        self.assertEqual((ob.name, ob.simiantype), ('anthony', 'punyhuman'))

        res = catalog.searchResults(simiantype='ape', name='bobo')
        self.assertEqual(len(res), 0)

        res = catalog.searchResults(simiantype='ape', name='mwumi')
        self.assertEqual(len(res), 0)
        self.assertRaises(ValueError, catalog.searchResults,
                          simiantype='monkey', hat='beret')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite


if __name__ == "__main__":
    unittest.main()

