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
This test suite tests all Validator methods with exception tothe ones defined
by IInstanceFactory, since they have their own test suite.

These tests are actually pretty boring, since almost nothing is implemented.
The action can be found in the Validators/ subdirectory/

$Id: testValidator.py,v 1.2 2002/06/10 23:27:50 jim Exp $
"""

import unittest
from Zope.App.Formulator.Validator import Validator
from Zope.App.Formulator.Errors import ValidationError


class Field:
    """Field stub"""

    id = 'id'
    
    def getErrorMessage(self, name):
        return "Unknown error: %s" % name


def extValidator(self, value):
    """External Validator stub."""
    return value


class Test( unittest.TestCase ):

    def _makeValidator(self):
        """Make a validator to test the functions with."""
        some_validator = Validator()
        return some_validator


    def testInit(self):
        """Test __init__ without passing a context."""
        some_validator = Validator(externalValidator=extValidator)
        self.assertEqual(some_validator.externalValidator, extValidator)


    def testValidate(self):
        """Test the validate method."""
        validator = self._makeValidator()
        self.assertEqual(validator.validate(Field(), 'data'), None)        


    def testRaiseError(self):
        """Test the raiseError method."""
        validator = self._makeValidator()
        self.failUnlessRaises(ValidationError, validator.raiseError, 'Key', Field())


    def testGetMessage(self):
        """Test the getMessage method."""
        validator = self._makeValidator()
        self.assertEqual(validator.getMessage('externalValidatorFailed'),
                         validator.externalValidatorFailed)
        self.assertEqual(validator.getMessage('foo'), None)


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )


if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )

