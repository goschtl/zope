##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for CMFCatalogAware.

$Id$
"""

import unittest
import Testing

import transaction
from AccessControl.SecurityManagement import newSecurityManager
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem

from zope.interface import implements

from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.exceptions import NotFound
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.testing import EventZCMLLayer
from Products.CMFCore.testing import TraversingZCMLLayer
from Products.CMFCore.tests.test_PortalFolder import _AllowedUser
from Products.CMFCore.tests.test_PortalFolder import _SensitiveSecurityPolicy
from Products.CMFCore.tests.base.testcase import LogInterceptor
from Products.CMFCore.tests.base.testcase import SecurityRequestTest

CMF_SECURITY_INDEXES = CMFCatalogAware._cmf_security_indexes

def physicalpath(ob):
    return '/'.join(ob.getPhysicalPath())


class SimpleFolder(Folder):
    def __init__(self, id):
        self._setId(id)

class DummyRoot(SimpleFolder):
    def getPhysicalRoot(self):
        return self

class DummyOldBrain:
    def __init__(self, ob, path):
        self.ob = ob
        self.id = ob.getId()
        self.path = path
    def getPath(self):
        return self.path
    def getObject(self):
        if self.id == 'missing':
            if self.ob.GETOBJECT_RAISES:
                raise NotFound("missing")
            else:
                return None
        if self.id == 'hop':
            raise ValueError("security problem for this object")
        return self.ob

class DummyBrain(DummyOldBrain):
    def _unrestrictedGetObject(self):
        if self.id == 'missing':
            return self.getObject()
        return self.ob

class DummyCatalog(SimpleItem):
    brain_class = DummyBrain
    def __init__(self):
        self.log = []
        self.obs = []
    def indexObject(self, ob):
        self.log.append('index %s' % physicalpath(ob))
    def reindexObject(self, ob, idxs=[], update_metadata=0, uid=None):
        self.log.append('reindex %s %s' % (physicalpath(ob), idxs))
    def unindexObject(self, ob):
        self.log.append('unindex %s' % physicalpath(ob))
    def setObs(self, obs):
        self.obs = [(ob, physicalpath(ob)) for ob in obs]
    def unrestrictedSearchResults(self, path):
        res = []
        for ob, obpath in self.obs:
            if not (obpath+'/').startswith(path+'/'):
                continue
            res.append(self.brain_class(ob, obpath))
        return res


class DummyWorkflowTool(SimpleItem):

    def __init__(self):
        self.log = []

    def notifyCreated(self, obj):
        self.log.append('created %s' % physicalpath(obj))


class TheClass(CMFCatalogAware, Folder):

    implements(IContentish)

    def __init__(self, id):
        self._setId(id)
        self.notified = False

    def notifyModified(self):
        self.notified = True


class CMFCatalogAwareTests(unittest.TestCase, LogInterceptor):

    layer = TraversingZCMLLayer

    def setUp(self):
        self.root = DummyRoot('')
        self.root.site = SimpleFolder('site')
        self.site = self.root.site
        self.site._setObject('portal_catalog', DummyCatalog())
        self.site._setObject('portal_workflow', DummyWorkflowTool())
        self.site.foo = TheClass('foo')

    def tearDown(self):
        self._ignore_log_errors()
        self._ignore_log_errors(subsystem='CMFCore.CMFCatalogAware')

    def test_indexObject(self):
        foo = self.site.foo
        cat = self.site.portal_catalog
        foo.indexObject()
        self.assertEquals(cat.log, ["index /site/foo"])

    def test_unindexObject(self):
        foo = self.site.foo
        cat = self.site.portal_catalog
        foo.unindexObject()
        self.assertEquals(cat.log, ["unindex /site/foo"])

    def test_reindexObject(self):
        foo = self.site.foo
        cat = self.site.portal_catalog
        foo.reindexObject()
        self.assertEquals(cat.log, ["reindex /site/foo []"])
        self.assert_(foo.notified)

    def test_reindexObject_idxs(self):
        foo = self.site.foo
        cat = self.site.portal_catalog
        foo.reindexObject(idxs=['bar'])
        self.assertEquals(cat.log, ["reindex /site/foo ['bar']"])
        self.failIf(foo.notified)

    def test_reindexObjectSecurity(self):
        foo = self.site.foo
        self.site.foo.bar = TheClass('bar')
        bar = self.site.foo.bar
        self.site.foo.hop = TheClass('hop')
        hop = self.site.foo.hop
        cat = self.site.portal_catalog
        cat.setObs([foo, bar, hop])
        foo.reindexObjectSecurity()
        l = list(cat.log)
        l.sort()
        self.assertEquals(l, [
            "reindex /site/foo %s"%str(CMF_SECURITY_INDEXES),
            "reindex /site/foo/bar %s"%str(CMF_SECURITY_INDEXES),
            "reindex /site/foo/hop %s"%str(CMF_SECURITY_INDEXES),
            ])
        self.failIf(foo.notified)
        self.failIf(bar.notified)
        self.failIf(hop.notified)

    def test_reindexObjectSecurity_missing_raise(self):
        # Exception raised for missing object (Zope 2.8 brains)
        foo = self.site.foo
        missing = TheClass('missing').__of__(foo)
        missing.GETOBJECT_RAISES = True
        cat = self.site.portal_catalog
        try:
            self._catch_log_errors()
            cat.setObs([foo, missing])
        finally:
            self._ignore_log_errors()
        self.assertRaises(NotFound, foo.reindexObjectSecurity)
        self.failIf( self.logged ) # no logging due to raise

    def test_reindexObjectSecurity_missing_noraise(self):
        # Raising disabled
        self._catch_log_errors(subsystem='CMFCore.CMFCatalogAware')
        foo = self.site.foo
        missing = TheClass('missing').__of__(foo)
        missing.GETOBJECT_RAISES = False
        cat = self.site.portal_catalog
        cat.setObs([foo, missing])
        foo.reindexObjectSecurity()
        self.assertEquals(cat.log,
                          ["reindex /site/foo %s"%str(CMF_SECURITY_INDEXES)])
        self.failIf(foo.notified)
        self.failIf(missing.notified)
        self.assertEqual( len(self.logged), 1 ) # logging because no raise

    def test_catalog_tool(self):
        foo = self.site.foo
        self.assertEqual(foo._getCatalogTool(), self.site.portal_catalog)

    def test_workflow_tool(self):
        foo = self.site.foo
        self.assertEqual(foo._getWorkflowTool(), self.site.portal_workflow)

    # FIXME: more tests needed


class CMFCatalogAware_CopySupport_Tests(SecurityRequestTest):

    layer = EventZCMLLayer

    def _makeSite(self):
        self.app._setObject('site', SimpleFolder('site'))
        site = self.app._getOb('site')
        site._setObject('portal_catalog', DummyCatalog())
        site._setObject('portal_workflow', DummyWorkflowTool())
        # Hack, we need a _p_mtime for the file, so we make sure that it
        # has one. We use a subtransaction, which means we can rollback
        # later and pretend we didn't touch the ZODB.
        transaction.savepoint(optimistic=True)
        return site

    def _initPolicyAndUser( self
                          , a_lambda=None
                          , v_lambda=None
                          , c_lambda=None
                          ):
        from AccessControl import SecurityManager

        def _promiscuous( *args, **kw ):
            return 1

        if a_lambda is None:
            a_lambda = _promiscuous

        if v_lambda is None:
            v_lambda = _promiscuous

        if c_lambda is None:
            c_lambda = _promiscuous

        scp = _SensitiveSecurityPolicy( v_lambda, c_lambda )
        SecurityManager.setSecurityPolicy( scp )
        newSecurityManager( None
                          , _AllowedUser(a_lambda).__of__(self.app.acl_users))

    def test_object_indexed_after_adding(self):

        site = self._makeSite()
        bar = TheClass('bar')
        site._setObject('bar', bar)
        cat = site.portal_catalog
        self.assertEquals(cat.log, ["index /site/bar"])

    def test_object_unindexed_after_removing(self):

        site = self._makeSite()
        bar = TheClass('bar')
        site._setObject('bar', bar)
        cat = site.portal_catalog
        cat.log = []
        site._delObject('bar')
        self.assertEquals(cat.log, ["unindex /site/bar"])

    def test_object_indexed_after_copy_and_pasting(self):

        self._initPolicyAndUser() # allow copy/paste operations
        site = self._makeSite()
        site.folder1 = SimpleFolder('folder1')
        folder1 = site.folder1
        site.folder2 = SimpleFolder('folder2')
        folder2 = site.folder2

        bar = TheClass('bar')
        folder1._setObject('bar', bar)
        cat = site.portal_catalog
        cat.log = []

        transaction.savepoint(optimistic=True)

        cookie = folder1.manage_copyObjects(ids=['bar'])
        folder2.manage_pasteObjects(cookie)

        self.assertEquals(cat.log, ["index /site/folder2/bar"])

    def test_object_reindexed_after_cut_and_paste(self):

        self._initPolicyAndUser() # allow copy/paste operations
        site = self._makeSite()
        site.folder1 = SimpleFolder('folder1')
        folder1 = site.folder1
        site.folder2 = SimpleFolder('folder2')
        folder2 = site.folder2

        bar = TheClass('bar')
        folder1._setObject('bar', bar)
        cat = site.portal_catalog
        cat.log = []

        transaction.savepoint(optimistic=True)

        cookie = folder1.manage_cutObjects(ids=['bar'])
        folder2.manage_pasteObjects(cookie)

        self.assertEquals(cat.log, ["unindex /site/folder1/bar",
                                    "reindex /site/folder2/bar []"])

    def test_object_reindexed_after_moving(self):

        self._initPolicyAndUser() # allow copy/paste operations
        site = self._makeSite()

        bar = TheClass('bar')
        site._setObject('bar', bar)
        cat = site.portal_catalog
        cat.log = []

        transaction.savepoint(optimistic=True)

        site.manage_renameObject(id='bar', new_id='baz')
        self.assertEquals(cat.log, ["unindex /site/bar",
                                    "reindex /site/baz []"])


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CMFCatalogAwareTests),
        unittest.makeSuite(CMFCatalogAware_CopySupport_Tests),
        ))

if __name__ == '__main__':
    from Products.CMFCore.testing import run
    run(test_suite())
