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
"""
$Id: test_delete.py,v 1.7 2003/09/21 17:32:17 jim Exp $
"""
__metaclass__ = type

from unittest import TestCase, TestSuite, makeSuite
import zope.app.http.delete
from zope.publisher.browser import TestRequest
from zope.app.interfaces.file import IWriteDirectory, IFileFactory
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.interface import implements
from zope.app.container.contained import contained

class Container:

    implements(IWriteDirectory, IFileFactory)

    def __delitem__(self, name):
        delattr(self, name)


class TestDelete(PlacelessSetup, TestCase):

    def test(self):
        container = Container()
        container.a = 'spam'
        item = contained(Container(), container, name='a')

        request = TestRequest()
        delete = zope.app.http.delete.DELETE(item, request)
        self.assert_(hasattr(container, 'a'))
        self.assertEqual(delete.DELETE(), '')
        self.assert_(not hasattr(container, 'a'))

def test_suite():
    return TestSuite((
        makeSuite(TestDelete),
        ))
