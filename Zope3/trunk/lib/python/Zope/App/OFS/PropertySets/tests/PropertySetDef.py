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
$Id: PropertySetDef.py,v 1.2 2002/06/10 23:28:09 jim Exp $
"""

from Interface.Verify import verifyObject
from Zope.App.OFS.PropertySets.IPropertySetDef import IPropertySetDef
from Zope.Exceptions import DuplicationError

class Field: pass

class PropertySetDef:
    "Test the IPropertySetDef interface"

    def setUp(self):
        self.field1 = Field()
        self.field2 = Field()
        self.psd.addField('test1',self.field1)
        self.psd.addField('test2',self.field2)

    def testInterfaceVerifies(self):
        verifyObject(IPropertySetDef,self.psd)

    def testStorage(self):
        """test __getitem__"""
        self.failUnlessEqual(self.field1,self.psd.getField('test1'))

    def testGetitemException(self):
        """test getField raises exception on unknown key"""
        self.assertRaises(KeyError,self.psd.getField,'randomkey')

    def testHas_field(self):
        self.failUnlessEqual(1,self.psd.has_field('test1'))
        self.failUnlessEqual(1,self.psd.has_field('test2'))

    def testfieldNames(self):
        self.failUnlessEqual(['test1','test2'],self.psd.fieldNames())

    def testIter(self):
        self.failUnlessEqual([self.field1,self.field2],
            list(self.psd.__iter__()))

    def testLen(self):
        self.failUnlessEqual(len(self.psd),2)

    def testAddDupField(self):
        self.assertRaises(DuplicationError,self.psd.addField,'test1',None)
