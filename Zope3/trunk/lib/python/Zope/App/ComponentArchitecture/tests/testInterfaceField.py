##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interface fields tests

$Id: testInterfaceField.py,v 1.2 2002/12/04 09:54:06 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
import Interface
from Zope.App.ComponentArchitecture.InterfaceField import InterfaceField
from Zope.Schema.Exceptions import ValidationError
        
class Test(TestCase):

    def test_validate(self):
        field = InterfaceField()
        
        field.validate(Interface.Interface)
        class I(Interface.Interface): pass
        field.validate(I)
        
        self.assertRaises(ValidationError, field.validate, Interface)
        class I: pass
        self.assertRaises(ValidationError, field.validate, I)

def test_suite():
    return TestSuite((makeSuite(Test),))

if __name__=='__main__':
    main(defaultTest='test_suite')

