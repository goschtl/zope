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
$Id: test_delete.py,v 1.1 2003/02/28 22:34:28 jim Exp $
"""
__metaclass__ = type

from unittest import TestCase, TestSuite, main, makeSuite
from StringIO import StringIO
import zope.app.http.delete
from zope.publisher.browser import TestRequest
from zope.app.interfaces.file import IWriteFile, IWriteDirectory, IFileFactory
from zope.app.interfaces.container import IZopeWriteContainer
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.proxy.context import ContextWrapper

class Container:

    __implements__ = IWriteDirectory, IZopeWriteContainer, IFileFactory

    def __delitem__(self, name):
        delattr(self, name)
        

class TestDelete(PlacelessSetup, TestCase):

    def test(self):
        container = Container()
        container.a = 'spam'
        item = ContextWrapper(Container(), container, name='a')
        
        request = TestRequest()
        delete = zope.app.http.delete.DELETE(item, request)
        self.assert_(hasattr(container, 'a'))        
        self.assertEqual(delete.DELETE(), '')
        self.assert_(not hasattr(container, 'a'))        

def test_suite():
    return TestSuite((
        makeSuite(TestDelete),
        ))
