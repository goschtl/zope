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

$Id: testDT_With.py,v 1.1 2002/06/25 15:37:17 srichter Exp $
"""

import unittest
from DTMLTestBase import DTMLTestBase 

class TestDT_With(DTMLTestBase):

    def testBasic(self):
        class person:
            name='Jim'
            height_inches=73

        result = self.doc_class("""<dtml-with person>
        Hi, my name is <dtml-var name>
        My height is <dtml-var "height_inches*2.54"> centimeters.
        </dtml-with>""")(person=person)

        expected = """        Hi, my name is Jim
        My height is 185.42 centimeters.
        """

        self.assertEqual(result, expected)
      
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest( unittest.makeSuite(TestDT_With) )
    return suite



if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
