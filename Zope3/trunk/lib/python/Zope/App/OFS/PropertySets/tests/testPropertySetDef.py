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

Revision information:
$Id: testPropertySetDef.py,v 1.2 2002/06/10 23:28:09 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup
from PropertySetDef import PropertySetDef as PropertySetDefTestClass
from Zope.App.OFS.PropertySets.PropertySetDef import PropertySetDef

class Field: pass

class Test(CleanUp, PropertySetDefTestClass, TestCase):
    
    def setUp(self):
        self.psd = PropertySetDef()
        #super(Test,self).setUp()
        PropertySetDefTestClass.setUp(self)
        CleanUp.setUp(self)


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
