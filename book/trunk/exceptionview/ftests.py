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
    
    def test_PaymentErrorView(self):
        response = self.publish("/raiseError.html", handle_errors=True)
  
        self.assertEqual(response.getStatus(), 402)
        body = response.getBody()
        self.assert_('402 - Payment Required' in body)
        self.assert_('payment to Stephan Richter' in body)
  
  
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))
  
if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
