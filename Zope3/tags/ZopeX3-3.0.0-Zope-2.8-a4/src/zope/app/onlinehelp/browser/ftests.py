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
"""Functional Tests for Onlinehelp

$Id$
"""
import os
import transaction
import unittest

from zope.app.folder.interfaces import IRootFolder
from zope.app.file import File
from zope.app.tests.functional import BrowserTestCase
from zope.app.onlinehelp.tests.test_onlinehelp import testdir
from zope.app.onlinehelp import help

class Test(BrowserTestCase):

    def test_contexthelp(self):
        path = os.path.join(testdir(), 'help.txt')
        help.registerHelpTopic('ui','help','Help',path,
             IRootFolder,
             None)
        path = os.path.join(testdir(), 'help2.txt')
        help.registerHelpTopic('ui','help2','Help2',path,
             IRootFolder,
             'contents.html')
        root = self.getRootFolder()
        root['file']=File()
        transaction.commit()

        response = self.publish(
            '/contents.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find(
            "javascript:popup('contents.html/++help++/@@contexthelp.html") >= 0)

        response = self.publish(
            '/contents.html/++help++/@@contexthelp.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find("This is another help!") >= 0)

        response = self.publish(
            '/index.html/++help++/@@contexthelp.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find("This is a help!") >= 0)

        response = self.publish(
            '/file/edit.html/++help++/@@contexthelp.html',
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find(
            "Welcome to the Zope 3 Online Help System.") >= 0)

        path = '/contents.html/++help++'
        response = self.publish(
            path,
            basic='mgr:mgrpw')

        self.assertEqual(response.getStatus(), 200)
        body = ' '.join(response.getBody().split())
        self.assert_(body.find(
            "Online Help - TOC") >= 0)

        self.checkForBrokenLinks(body, path, basic='mgr:mgrpw')


def test_suite():
    return unittest.makeSuite(Test)

if __name__ == '__main__':
    unittest.main()
