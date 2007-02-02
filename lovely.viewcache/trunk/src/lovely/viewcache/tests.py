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
"""
$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
from zope import component
import zope.interface
import zope.security
from zope.testing import doctest
from zope.app.folder import rootFolder
from zope.app.publication.zopepublication import ZopePublication
from zope.testing.doctestunit import DocTestSuite, DocFileSuite
from zope.app.testing import setup
import ZODB.tests.util, transaction
from ZODB.interfaces import IDatabase
from zope.schema.interfaces import IVocabularyFactory
from lovely.mount.vocabulary import DatabaseVocabulary
from zope.app.schema import vocabulary

from zope.app.testing.setup import (placefulSetUp,
                                    placefulTearDown)


def setUp(test):
    root = placefulSetUp(site=True)
    test.globs['root'] = root

def setUpZODB(test):
    setUp(test)
    databases = {}
    db1 = ZODB.tests.util.DB(databases=databases, database_name='1')
    db2 = ZODB.tests.util.DB(databases=databases, database_name='2')
    test.db1 = db1
    test.db2 = db2
    cx = db1.open()
    root = cx.root()
    test.root_folder = rootFolder()
    root[ZopePublication.root_name] = test.root_folder
    test.globs['root'] = test.root_folder
    transaction.commit()
    vocabulary._clear()
    component.provideUtility(DatabaseVocabulary, IVocabularyFactory, 
                             name="Database Names")
    test.globs['db'] = db1

def tearDown(test):
    placefulTearDown()

def tearDownZODB(test):
    test.db1.close()
    test.db2.close()
    tearDown(test)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('manager.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('ram.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('zodb.txt',
                     setUp=setUpZODB, tearDown=tearDownZODB,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
