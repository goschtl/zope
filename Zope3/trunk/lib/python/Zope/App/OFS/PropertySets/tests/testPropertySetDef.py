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
$Id: testPropertySetDef.py,v 1.3 2002/07/16 22:54:03 jeremy Exp $
"""

from unittest import TestCase, main, makeSuite
from Zope.App.OFS.PropertySets.tests.PropertySetDef \
     import PropertySetDefTest
from Zope.App.OFS.PropertySets.PropertySetDef import PropertySetDef

class Field:
    pass

class Test(PropertySetDefTest, TestCase, object):
    
    def setUp(self):
        self.psd = PropertySetDef()
        super(Test, self).setUp()

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
