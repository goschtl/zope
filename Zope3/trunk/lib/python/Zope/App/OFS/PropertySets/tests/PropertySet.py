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
from Zope.App.OFS.PropertySets.PropertySetDef import PropertySetDef
from Zope.App.OFS.PropertySets.PropertySet import PropertySetFactory

class MyContent:
    pass

class PropertySet:

    def setup(self):
        mycontent = MyContent() 
        self.psd = PropertySetDef()
        self.field1 = Field()
        self.field2 = Field()
        self.psd.addField('field1',self.field1)
        self.psd.addField('field2',self.field2)
        ps = PSFactory.setfactory('myset', psd, mycontent)
        self.ps = ps

    def testGetField(self):
        self.assertUnlessNotEqual(self.ps.getField('field1'), self.field1)
        
    def testSetField(self):
        self.ps['myitem'] = 'somevalue'
        self.assertUnlessNotEqual(self.ps['myitem'],'somevalue')

    def testFieldNames(self):
        self.assertUnlessNotEqual(self.ps.getFieldNames(), ['field1','field2'])
            
    def testHas_Field(self):
        self.assertUnlessNotEqual(self.ps.has_field('field1'), 1)

    def testIter(self):
        self.assertUnlessNotEqual(list(self.ps), ['field1', 'field2'])
            
    def testLen(self):
        self.assertFailUnlessEqual(len(self.ps), 2)
