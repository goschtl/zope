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
This test suite tests the functionality of the PropertyFieldAdapter. This test
will actually depend on the Field class, but the required ContentObject is
implemented as a stub.

$Id: testPropertyFieldAdapter.py,v 1.3 2002/07/16 22:55:30 jeremy Exp $
"""

import unittest
from Zope.App.Formulator.PropertyFieldAdapter import PropertyFieldAdapter
from Zope.App.Formulator.Fields.Generic.StringField import StringField

DataField = StringField(id='data',
                        title='Data of Content Object',
                        description='This field represents the data...',
                        default='')


class ContentObject:
    """Content Obejct stub."""

    data = ''

    def setData(self, data):
        """Set the data property."""
        self.data = data


    def getData(self):
        """Get the data property."""
        return self.data



class Test(unittest.TestCase):


##    def testAdapterRegistry(self):
##        """Test somehow whether the PropertyFieldAdapter was correctly
##           registered"""

##        # XXX I do not know how to do these tests yet.


    def testSetData(self):
        """Test setting the data in the ContentObject."""

        content = ContentObject()
        field = DataField(content)
        adapter = PropertyFieldAdapter(field)

        adapter.setPropertyInContext('Some Data')
        self.assertEqual(content.data, 'Some Data')


    def testGetData(self):
        """Test getting the data from the ContentObject."""

        content = ContentObject()
        content.data = 'Some Data'
        field = DataField(content)
        adapter = PropertyFieldAdapter(field)

        self.assertEqual(adapter.getPropertyInContext(), 'Some Data')
        


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())

