##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 72084 2007-01-18 01:02:26Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

import doctest
import unittest
from zope import component
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore
from doctest import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope.app.keyreference.testing import SimpleKeyReference
from lovely.relation import configurator


def setUp(test):
    root = setup.placefulSetUp(True)
    test.globs['root'] = root
    util = configurator.SetUpO2OStringTypeRelationships(root)
    util({})
    component.provideAdapter(SimpleKeyReference)
    component.provideAdapter(ZDCAnnotatableAdapter,
                             provides=IWriteZopeDublinCore)
    intids = IntIds()
    component.provideUtility(intids, IIntIds)

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite(
            (DocFileSuite('README.txt',
                         setUp=setUp,tearDown=tearDown,
                         optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                         ),
            )
            )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
