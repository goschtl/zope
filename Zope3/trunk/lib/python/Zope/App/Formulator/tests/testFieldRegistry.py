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
I do not think it is necessary to do the entire SimpleRegistry tests again.
Instead we will test whether the module in itself works.

$Id: testFieldRegistry.py,v 1.2 2002/06/10 23:27:50 jim Exp $
"""

import unittest
from Interface import Interface
from Zope.App.Formulator.FieldRegistry import registerField, getField, IField

class Field:
    """Field Stub."""

    __implements__ = IField



class Test( unittest.TestCase ):


    def testRegistry(self):

        field = Field()

        registerField('field', field)
        self.assertEqual(getField('field'), field)
        

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )


if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )

