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
"""Functional tests for Payment Exception view

$Id$
"""
import unittest

from zope.app.tests.functional import BrowserTestCase


class Test(BrowserTestCase):
    
    def test_RedirectManageHtml(self):
        response = self.publish("/manage.html")
        
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'), 'manage')
  

def test_suite():
    return unittest.makeSuite(Test)
  
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
