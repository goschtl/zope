##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Functional Tests for Class Documentation Module.

$Id: ftests.py,v 1.3 2004/04/06 20:57:59 jim Exp $
"""
import unittest
from zope.app.tests.functional import BrowserTestCase

class ClassModuleTests(BrowserTestCase):
    """Just a couple of tests ensuring that the templates render."""

    def testMenu(self):
        response = self.publish('/++apidoc++/Class/menu.html', 
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Browse Zope Source') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Class/menu.html',
                                 basic='mgr:mgrpw')

    def testMenuClassFinder(self):
        response = self.publish('/++apidoc++/Class/menu.html',
                                basic='mgr:mgrpw',
                                form={'path': 'Class', 'SUBMIT': 'Find'})
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('zope.app.apidoc.classmodule.ClassModule') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Class/menu.html',
                                 basic='mgr:mgrpw')

    def testModuleDetailsView(self):
        response = self.publish('/++apidoc++/Class/zope/app/apidoc/',
                                basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Zope 3 API Documentation') > 0)
        self.checkForBrokenLinks(body, '/++apidoc++/Class/zope/app/apidoc/',
                                 basic='mgr:mgrpw')

    def testClassDetailsView(self):
        response = self.publish(
            '/++apidoc++/Class/zope/app/apidoc/APIDocumentation',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('Represent the complete API Documentation.') > 0)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Class/zope/app/apidoc/APIDocumentation',
            basic='mgr:mgrpw')

    def testFunctionDetailsView(self):
        response = self.publish(
            '/++apidoc++/Class/zope/app/apidoc/handleNamespace',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(body.find('handleNamespace(name, parameters, pname,') > 0)
        self.checkForBrokenLinks(
            body, '/++apidoc++/Class/zope/app/apidoc/handleNamesapce',
            basic='mgr:mgrpw')
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ClassModuleTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
