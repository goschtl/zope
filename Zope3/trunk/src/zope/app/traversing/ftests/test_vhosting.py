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
"""Functional tests for virtual hosting.

$Id: test_vhosting.py,v 1.9 2003/09/21 17:33:46 jim Exp $
"""

import unittest
from zope.testing.functional import BrowserTestCase
from zope.app.content.zpt import ZPTPage
from zope.app.content.folder import Folder
from transaction import get_transaction
from zope.component.resource import provideResource
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.publisher.browser.resource import Resource
from zope.app.traversing import traverse
from zope.security.checker import defineChecker, NoProxy
from zope.app.container.contained import Contained

__metaclass__ = type

class MyObj(Contained):
    def __getitem__(self, key):
        return traverse(self, '/foo/bar/' + key)

defineChecker(MyObj, NoProxy)

class TestVirtualHosting(BrowserTestCase):

    def test_request_url(self):
        self.addPage('/pt', u'<span tal:replace="request/URL"/>')
        self.verify('/pt', 'http://localhost/pt/index.html\n')
        self.verify('/++vh++/++/pt',
                    'http://localhost/pt/index.html\n')
        self.verify('/++vh++https:otherhost:443/++/pt',
                    'https://otherhost/pt/index.html\n')
        self.verify('/++vh++https:otherhost:443/fake/folders/++/pt',
                    'https://otherhost/fake/folders/pt/index.html\n')

        self.addPage('/foo/bar/pt', u'<span tal:replace="request/URL"/>')
        self.verify('/foo/bar/pt', 'http://localhost/foo/bar/pt/index.html\n')
        self.verify('/foo/bar/++vh++/++/pt',
                    'http://localhost/pt/index.html\n')
        self.verify('/foo/bar/++vh++https:otherhost:443/++/pt',
                    'https://otherhost/pt/index.html\n')
        self.verify('/foo/++vh++https:otherhost:443/fake/folders/++/bar/pt',
                    'https://otherhost/fake/folders/bar/pt/index.html\n')

    def test_request_base(self):
        self.addPage('/pt', u'<head></head>')
        self.verify('/pt',
                    '<head>\n<base href="http://localhost/pt/index.html" />\n'
                    '</head>\n')
        self.verify('/++vh++/++/pt',
                    '<head>\n<base href="http://localhost/pt/index.html" />\n'
                    '</head>\n')
        self.verify('/++vh++https:otherhost:443/++/pt',
                    '<head>\n'
                    '<base href="https://otherhost/pt/index.html" />'
                    '\n</head>\n')
        self.verify('/++vh++https:otherhost:443/fake/folders/++/pt',
                    '<head>\n<base href='
                    '"https://otherhost/fake/folders/pt/index.html" />'
                    '\n</head>\n')

        self.addPage('/foo/bar/pt', u'<head></head>')
        self.verify('/foo/bar/pt',
                    '<head>\n<base '
                    'href="http://localhost/foo/bar/pt/index.html" />\n'
                    '</head>\n')
        self.verify('/foo/bar/++vh++/++/pt',
                    '<head>\n<base href="http://localhost/pt/index.html" />\n'
                    '</head>\n')
        self.verify('/foo/bar/++vh++https:otherhost:443/++/pt',
                    '<head>\n'
                    '<base href="https://otherhost/pt/index.html" />'
                    '\n</head>\n')
        self.verify('/foo/++vh++https:otherhost:443/fake/folders/++/bar/pt',
                    '<head>\n<base href='
                    '"https://otherhost/fake/folders/bar/pt/index.html" />'
                    '\n</head>\n')

    def test_request_redirect(self):
        self.addPage('/foo/index.html', u'Spam')
        self.verifyRedirect('/foo', 'http://localhost/foo/index.html')
        self.verifyRedirect('/++vh++https:otherhost:443/++/foo',
                            'https://otherhost/foo/index.html')
        self.verifyRedirect('/foo/++vh++https:otherhost:443/bar/++',
                            'https://otherhost/bar/index.html')

    def test_absolute_url(self):
        self.addPage('/pt', u'<span tal:replace="template/@@absolute_url"/>')
        self.verify('/pt', 'http://localhost/pt\n')
        self.verify('/++vh++/++/pt',
                    'http://localhost/pt\n')
        self.verify('/++vh++https:otherhost:443/++/pt',
                    'https://otherhost/pt\n')
        self.verify('/++vh++https:otherhost:443/fake/folders/++/pt',
                    'https://otherhost/fake/folders/pt\n')

        self.addPage('/foo/bar/pt',
                     u'<span tal:replace="template/@@absolute_url"/>')
        self.verify('/foo/bar/pt', 'http://localhost/foo/bar/pt\n')
        self.verify('/foo/bar/++vh++/++/pt',
                    'http://localhost/pt\n')
        self.verify('/foo/bar/++vh++https:otherhost:443/++/pt',
                    'https://otherhost/pt\n')
        self.verify('/foo/++vh++https:otherhost:443/fake/folders/++/bar/pt',
                    'https://otherhost/fake/folders/bar/pt\n')

    def test_absolute_url_absolute_traverse(self):
        self.createObject('/foo/bar/obj', MyObj())
        self.addPage('/foo/bar/pt',
                     u'<span tal:replace="container/obj/pt/@@absolute_url"/>')
        self.verify('/foo/bar/pt', 'http://localhost/foo/bar/pt\n')
        self.verify('/foo/++vh++https:otherhost:443/++/bar/pt',
                    'https://otherhost/bar/pt\n')

    def test_resources(self):
        provideResource('quux', IBrowserPresentation, Resource)
        self.addPage('/foo/bar/pt',
                     u'<span tal:replace="context/++resource++quux" />')
        self.verify('/foo/bar/pt', 'http://localhost/@@/quux\n')
        self.verify('/foo/++vh++https:otherhost:443/fake/folders/++/bar/pt',
                    'https://otherhost/fake/folders/@@/quux\n')

    def createFolders(self, path):
        """addFolders('/a/b/c/d') would traverse and/or create three nested
        folders (a, b, c) and return a tuple (c, 'd') where c is a Folder
        instance at /a/b/c."""
        folder = self.getRootFolder()
        if path[0] == '/':
            path = path[1:]
        path = path.split('/')
        for id in path[:-1]:
            try:
                folder = folder[id]
            except KeyError:
                folder[id] = Folder()
                folder = folder[id]
        return folder, path[-1]

    def createObject(self, path, obj):
        folder, id = self.createFolders(path)
        folder[id] = obj
        get_transaction().commit()

    def addPage(self, path, content):
        page = ZPTPage()
        page.source = content
        self.createObject(path, page)

    def verify(self, path, content):
        result = self.publish(path)
        self.assertEquals(result.getStatus(), 200)
        self.assertEquals(result.getBody(), content)

    def verifyRedirect(self, path, location):
        result = self.publish(path)
        self.assertEquals(result.getStatus(), 302)
        self.assertEquals(result.getHeader('Location'), location)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestVirtualHosting))
    return suite


if __name__ == '__main__':
    unittest.main()
