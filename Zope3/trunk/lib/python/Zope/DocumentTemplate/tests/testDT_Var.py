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

$Id: testDT_Var.py,v 1.2 2002/12/20 19:34:45 bwarsaw Exp $
"""

# XXX Don't normalize whitespace in this file -- the tests depend on the
# whitespace in the triple quoted strings.

import unittest
from Zope.DocumentTemplate import String
from DTMLTestBase import DTMLTestBase, dict, ObjectStub 

class TestDT_Var(DTMLTestBase):

    def testFmt(self):
        html = self.doc_class (
            '''<dtml-var spam fmt="$%.2f bob\'s your uncle"
                              null="spam%eggs!|">''') 

        self.assertEqual(html(spam=42), '$42.00 bob\'s your uncle')
        self.assertEqual(html(spam=None), 'spam%eggs!|')

    def testDefaultFmt(self):
        #import Missing
        html = self.doc_class (
            """
                      <dtml-var spam >
            html:     <dtml-var spam fmt=html-quote>
            url:      <dtml-var spam fmt=url-quote>
            multi:    <dtml-var spam fmt=multi-line>
            dollars:  <dtml-var spam fmt=whole-dollars>
            cents:    <dtml-var spam fmt=dollars-and-cents>
            dollars,: <dtml-var spam fmt=dollars-with-commas>
            cents,:   <dtml-var spam fmt=dollars-and-cents-with-commas>
    
            """)
    
        result1 = (
            """
                      4200000
            html:     4200000
            url:      4200000
            multi:    4200000
            dollars:  $4200000
            cents:    $4200000.00
            dollars,: $4,200,000
            cents,:   $4,200,000.00
    
            """)
    
        result2 = (
            """
                      None
            html:     None
            url:      None
            multi:    None
            dollars:  
            cents:    
            dollars,: 
            cents,:   
    
            """)
        
        result3 = (
            """
                      <a href="spam">\nfoo bar
            html:     &lt;a href=&quot;spam&quot;&gt;\nfoo bar
            url:      %3Ca%20href%3D%22spam%22%3E%0Afoo%20bar
            multi:    <a href="spam"><br>\nfoo bar
            dollars:  
            cents:    
            dollars,: 
            cents,:   
    
            """)

        self.assertEqual(html(spam=4200000), result1)
        self.assertEqual(html(spam=None), result2)
        self.assertEqual(html(spam='<a href="spam">\nfoo bar'), result3)


    def testRender(self):
       # Test automatic rendering of callable objects
       class C:
          x = 1
          def y(self): return self.x * 2
          h = self.doc_class("The h method, <dtml-var x> <dtml-var y>")
          h2 = self.doc_class("The h2 method")

       res1 = self.doc_class("<dtml-var x>, <dtml-var y>, <dtml-var h>")(C())
       res2 = self.doc_class(
          """
          <dtml-var expr="_.render(i.x)">,
          <dtml-var expr="_.render(i.y)">,
          
          <dtml-var expr="_.render(i.h2)">""")(i=C())

       expected = '1, 2, The h method, 1 2'
       expected2 = (
           """
          1,
          2,
          
          The h2 method""")

       self.assertEqual(res1, expected)
       self.assertEqual(res2, expected2)
       

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDT_Var))
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
