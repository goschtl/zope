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
"""

$Id: testNames.py,v 1.2 2002/06/10 23:29:24 jim Exp $
"""

import unittest, sys

class NameTest(unittest.TestCase):

    def setUp(self):

        from Zope.Configuration.tests import Products_
        self.old=sys.modules.get('ZopeProducts', None)
        sys.modules['ZopeProducts']=Products_

    def tearDown(self):
        old=self.old
        if old is None: del sys.modules['ZopeProducts']
        else: sys.modules['ZopeProducts']=self.old
        
    def testProductPath(self):
        from Zope.Configuration.name import resolve

        c=resolve('.Contact.')
        self.assertEquals(c.n, 2)
        c=resolve('ZopeProducts.Contact.Contact.Contact')
        self.assertEquals(c.n, 2)
        
    def testPackagePath(self):
        from Zope.Configuration.name import resolve

        c=resolve('Zope.Configuration.tests.Contact')
        import Zope.Configuration.tests.Contact
        self.assertEquals(c, Zope.Configuration.tests.Contact)

        c=resolve('Zope.Configuration.tests.Contact.')
        self.assertEquals(c.n, 1)
        c=resolve('Zope.Configuration.tests.Contact.Contact.Contact')
        self.assertEquals(c.n, 1)
        
    def testNoDots(self):
        from Zope.Configuration.name import resolve
        import Zope
        c=resolve('Zope')

        self.assertEquals(id(c), id(Zope))
        
    def testPackage(self):
        from Zope.Configuration.name import resolve
        c=resolve('Zope.App.ZMI')
        import Zope.App.ZMI

        self.assertEquals(id(c), id(Zope.App.ZMI))

    nameSet={
        ('Zope.Configuration.tests','Noplace'):'Zope.Configuration.tests',
        ('Zope.Configuration.tests.tests','Noplace'):'Zope.Configuration.tests+',
        ('Zope.Configuration.tests.tests.tests','Noplace'):'Zope.Configuration.tests+',
        ('Zope.Configuration.tests.tests.tests.','Noplace'):'Zope.Configuration.tests+',
        ('Zope.Configuration.tests+','Noplace'):'Zope.Configuration.tests+',
        ('Zope.Configuration.tests.tests.tests+','Noplace'):'Zope.Configuration.tests+',
        ('Zope.Configuration.tests.','Noplace'):'Zope.Configuration.tests+',
        ('.tests','Zope.Configuration'):'Zope.Configuration.tests',
        ('.tests.tests','Zope.Configuration'):'Zope.Configuration.tests+',
        ('.tests.tests.tests','Zope.Configuration'):'Zope.Configuration.tests+',
        ('.tests.tests.tests.','Zope.Configuration'):'Zope.Configuration.tests+',
        ('.tests+','Zope.Configuration'):'Zope.Configuration.tests+',
        ('.tests.tests.tests+','Zope.Configuration'):'Zope.Configuration.tests+',
        ('.tests.','Zope.Configuration'):'Zope.Configuration.tests+'
        }
    
    def testNormalizedName(self):
        from Zope.Configuration.name import getNormalizedName
        for args in self.nameSet:
            self.assertEquals(self.nameSet[args], getNormalizedName(*args))

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(NameTest)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
