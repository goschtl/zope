##############################################################################
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""
$Id: test_external_edit.py,v 1.1 2004/02/27 14:23:17 philikon Exp $
"""

import unittest
from base64 import encodestring

from zope.interface import implements, Interface, directlyProvides
from zope.publisher.browser import TestRequest

from zope.app import zapi
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.tests import ztapi
from zope.app.container.contained import contained
from zope.app.interfaces.content import IContentType
from zope.app.interfaces.file import IReadFile
from zope.app.file.file import File, FileReadFile

from zope.app.externaleditor.interfaces import IExternallyEditable
from zope.app.externaleditor.browser import ExternalEditor

class IEditableFile(Interface): pass

class ReadFileAdapter(FileReadFile):

    def getContentType(self):
        return self.context.getContentType()

    def setContentType(self, ct):
        self.context.setContentType(ct)

    contentType = property(getContentType, setContentType)

class EditableFile(File):
    """An editable file"""
    implements(IExternallyEditable, IEditableFile)

class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        ztapi.browserView(IExternallyEditable, 'external_edit', ExternalEditor)
        ztapi.provideAdapter(IExternallyEditable, IReadFile, ReadFileAdapter)
        directlyProvides(IEditableFile, IContentType)

    def test_external_edit(self):
        basic = 'Basic %s' % encodestring('%s:%s' % ('testuser', 'testpass'))
        env = {'HTTP_AUTHORIZATION':
               basic}
        request = TestRequest(environ=env)
        container = zapi.traverse(self.rootFolder, 'folder1')
        file = EditableFile('Foobar', 'text/plain')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.getData(), 'Foobar')
        file = contained(file, container, 'file')
        view = zapi.queryView(file, 'external_edit', request, None)
        self.failIf(view is None)
        expected = """\
url:http://127.0.0.1/folder1/file
content_type:text/plain
meta_type:IEditableFile
auth:%s
cookie:

Foobar""" % basic[:-1]
        self.assertEqual(view(), expected)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__ == '__main__':
    unittest.main()
