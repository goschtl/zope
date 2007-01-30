##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""test setup

$Id$
"""
__docformat__ = "reStructuredText"

import doctest
import unittest
import ZODB.tests.util, transaction
from zope import component
from zope.app.folder import rootFolder
from zope.app.publication.zopepublication import ZopePublication
from zope.app.testing import setup
from zope.testing.doctestunit import DocFileSuite
from ZODB.interfaces import IDatabase
from zope.schema.interfaces import IVocabularyFactory
from vocabulary import DatabaseVocabulary

from zope.app.schema import vocabulary


def setUpBasic(test):
    vocabulary._clear()
    component.provideUtility(DatabaseVocabulary, IVocabularyFactory, 
                             name="Database Names")

def setUp(test):
    setup.placefulSetUp()
    setUpBasic(test)    
    databases = {}
    db1 = ZODB.tests.util.DB(databases=databases, database_name='1')
    db2 = ZODB.tests.util.DB(databases=databases, database_name='2')
    component.provideUtility(db1, IDatabase, '1')
    component.provideUtility(db2, IDatabase, '2')
    test.db1 = db1
    test.db2 = db2
    cx = db1.open()
    root = cx.root()
    test.root_folder = rootFolder()
    root[ZopePublication.root_name] = test.root_folder
    transaction.commit()
    cx.close()
    test.globs['root'] = test.root_folder

def tearDown(test):
    setup.placefulTearDown()
    test.db1.close()
    test.db2.close()


def test_suite():

    return unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     setUp=setUpBasic,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('container.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
