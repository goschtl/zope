##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testRow.py,v 1.1 2002/06/25 15:41:46 k_vertigo Exp $
"""

from Zope.App.RDB.Row import row_class_factory
from Zope.Security.Proxy import ProxyFactory
from Zope.Exceptions import ForbiddenAttribute

from unittest import TestCase, TestSuite, main, makeSuite

class RowTests(TestCase):

    def test_row_klass_creation(self):

        columns = ('food', 'name')
        data = ('pizza', 'john')
        
        klass = row_class_factory(columns)
        ob = klass(data)
        
        self.failUnless(ob.food == 'pizza',
                        """bad row class attribute""")

        self.failUnless(ob.name == 'john',
                        """bad row class attribute (2)""")        

    def test_row_klass_security_declarations(self):

        columns = ('type', 'speed')
        data = ('airplane', '800km')
        
        klass = row_class_factory(columns)

        ob = klass(data)

        proxied = ProxyFactory(ob)

        self.failUnless (proxied.type == 'airplane',
                         """ security proxy error""")

        self.failUnless (proxied.speed == '800km',
                         """ security proxy error (2)""")        

        self.assertRaises(ForbiddenAttribute,
                          lambda x=proxied: x.__slots__
                          )

def test_suite():
    return TestSuite((
        makeSuite(RowTests),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
