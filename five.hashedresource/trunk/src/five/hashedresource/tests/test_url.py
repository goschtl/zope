##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""tests

$Id$
"""
from five.hashedresource import testing
import Products.Five.browser.resource
import os.path
import unittest
import zope.component
import zope.traversing.browser.interfaces


class HashingURLTest(testing.FunctionalTestCase):

    def test_directory_url_should_contain_hash(self):
        directory_url = str(zope.component.getMultiAdapter(
                (self.directory, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertMatches(
            r'http://127.0.0.1/\+\+noop\+\+[^/]*/\+\+resource\+\+%s' %
            self.dirname, directory_url)

    def test_file_url_should_contain_hash(self):
        file = Products.Five.browser.resource.FileResourceFactory(
            'test.txt', os.path.join(testing.fixture, 'test.txt'))(
            self.request)
        file.__name__ = 'test.txt'
        file.absolute_url = lambda: 'http://127.0.0.1'
        file_url = str(zope.component.getMultiAdapter((file, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertMatches(
            'http://127.0.0.1/\+\+noop\+\+[^/]*/\+\+resource\+\+test.txt',
            file_url)

    def test_different_files_hashes_should_differ(self):
        file1 = Products.Five.browser.resource.FileResourceFactory(
            'test.txt', os.path.join(testing.fixture, 'test.txt'))(
            self.request)
        file1.__name__ = 'test.txt'
        file1.absolute_url = lambda: 'http://127.0.0.1'
        file1_url = str(zope.component.getMultiAdapter((file1, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        file2 = Products.Five.browser.resource.FileResourceFactory(
            'test.txt', os.path.join(testing.fixture, 'test.pt'))(
            self.request)
        file2.__name__ = 'test.txt'
        file2.absolute_url = lambda: 'http://127.0.0.1'
        file2_url = str(zope.component.getMultiAdapter((file2, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertNotEqual(self._hash(file1_url), self._hash(file2_url))

    def test_directory_contents_changed_hash_should_change(self):
        before = str(zope.component.getMultiAdapter(
                (self.directory, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('foo')
        after = str(zope.component.getMultiAdapter(
                (self.directory, self.request),
                zope.traversing.browser.interfaces.IAbsoluteURL))
        self.assertNotEqual(self._hash(before), self._hash(after))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HashingURLTest))
    return suite
