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

$Id: test_names.py,v 1.2 2002/12/25 14:13:34 jim Exp $
"""

import unittest, sys

class NameTest(unittest.TestCase):

    def setUp(self):

        from zope.configuration.tests import products_
        self.old = sys.modules.get('zopeproducts', None)
        sys.modules['zopeproducts'] = products_

    def tearDown(self):
        old = self.old
        if old is None:
            del sys.modules['zopeproducts']
        else:
            sys.modules['zopeproducts']=self.old

    def testProductPath(self):
        from zope.configuration.name import resolve

        c=resolve('.contact.contact.Contact')
        self.assertEquals(c.n, 2)
        c=resolve('zopeproducts.contact.contact.Contact')
        self.assertEquals(c.n, 2)

    def testPackagePath(self):
        from zope.configuration.name import resolve

        c=resolve('zope.configuration.tests.contact')
        import zope.configuration.tests.contact
        self.assertEquals(c, zope.configuration.tests.contact)

        c=resolve('zope.configuration.tests.contact.contact.Contact')
        self.assertEquals(c.n, 1)
        c=resolve('zope.configuration.tests.contact.contact.Contact')
        self.assertEquals(c.n, 1)

    def testNoDots(self):
        from zope.configuration.name import resolve
        import zope
        c=resolve('zope')

        self.assertEquals(id(c), id(zope))

    def testPackage(self):
        from zope.configuration.name import resolve
        c=resolve('zope.configuration.tests')
        import zope.configuration.tests

        self.assertEquals(id(c), id(zope.configuration.tests))

    nameSet={
        ('zope.configuration.tests','Noplace'):
        'zope.configuration.tests',
        ('zope.configuration.tests.tests','Noplace'):
        'zope.configuration.tests+',
        ('zope.configuration.tests.tests.tests','Noplace'):
        'zope.configuration.tests+',
        ('zope.configuration.tests.tests.tests.','Noplace'):
        'zope.configuration.tests+',
        ('zope.configuration.tests+','Noplace'):
        'zope.configuration.tests+',
        ('zope.configuration.tests.tests.tests+','Noplace'):
        'zope.configuration.tests+',
        ('zope.configuration.tests.','Noplace'):
        'zope.configuration.tests+',
        ('.tests','zope.configuration'):
        'zope.configuration.tests',
        ('.tests.tests','zope.configuration'):
        'zope.configuration.tests+',
        ('.tests.tests.tests','zope.configuration'):
        'zope.configuration.tests+',
        ('.tests.tests.tests.','zope.configuration'):
        'zope.configuration.tests+',
        ('.tests+','zope.configuration'):
        'zope.configuration.tests+',
        ('.tests.tests.tests+','zope.configuration'):
        'zope.configuration.tests+',
        ('.tests.','zope.configuration'):
        'zope.configuration.tests+'
        }

    def testNormalizedName(self):
        from zope.configuration.name import getNormalizedName
        for args in self.nameSet:
            self.assertEquals(self.nameSet[args], getNormalizedName(*args))

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(NameTest)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
