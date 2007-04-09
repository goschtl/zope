##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Doctest tests

$Id$
"""
import unittest

from zope.interface import implements
from zope.testing import doctest
from zope.app.testing import placelesssetup

from zope.app.appsetup.interfaces import IApplicationFactory

class ApplicationFactoryStub:

    implements(IApplicationFactory)

    def prepare(self):
        print "Prepare called"

    def __call__(self, request):
        print "__call__ called"

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(
        'zope.app.appsetup.appsetup',
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown))
    suite.addTest(doctest.DocFileSuite('schema.txt',
        optionflags=doctest.ELLIPSIS))
    suite.addTest(doctest.DocFileSuite(
        'bootstrap.txt',
        setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
        ))
    return suite

if __name__ == '__main__':
    unittest.main()
