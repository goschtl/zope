##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""Document Template Tests

$Id: testDT_Try.py,v 1.1 2002/06/25 15:37:17 srichter Exp $
"""

import unittest
from Zope.DocumentTemplate import String
from DTMLTestBase import DTMLTestBase 

class TestDT_Try(DTMLTestBase):

    def testBasic(self):

        html = self.doc_class(
            """
            <dtml-try>
              foo = <dtml-var value>
            <dtml-except>
              There is no bar variable.
            </dtml-try>
            """)

        result1 = "foo = bar"
        result2 = "There is no bar variable."

        self.assertEqual(html(value='bar').strip(), result1.strip())
        self.assertEqual(html().strip(), result2.strip())
      
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(TestDT_Try))
    return suite



if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
