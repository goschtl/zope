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

$Id: testValidators.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

import unittest
from Zope.App.Formulator import Errors


class TestField:
    """Class to provide a stub for a field"""

    id = 'test'
    isRequired = 0

    def getValue(self, id):
        return getattr(self, id)

    def getErrorMessage(self, errorKey):
        return "Nothing"

field = TestField()


class ValidatorTestCase(unittest.TestCase):
    def assertValidatorRaises(self, exception, error_key, f, args=[], kw={}):
        try:
            apply(f, args, kw)
        except Errors.ValidationError, e:
            if e.errorKey != error_key:
                self.fail('Got wrong error. Expected %s received %s' %
                          (error_key, e))
            else:
                return
        self.fail('Expected error %s but no error received.' % error_key)



class StringValidatorTestCase(ValidatorTestCase):
    """Test String Validator Cases"""
    
    def setUp(self):
        from Zope.App.Formulator.Validators import StringValidator
        self.v = StringValidator.StringValidator()


    def testBasic(self):
        self.assertEqual(self.v.validate(field, 'Foo'), 'Foo')


    def testStripWhitespace(self):
        self.assertEqual(self.v.validate(field, '  Foo  '), 'Foo')


    def testErrorTooLong(self):    
        self.v.maxLength = 10
        self.assertValidatorRaises(Errors.ValidationError, 'tooLong',
                                   self.v.validate,
                                   (field, 'This is a much longer text.'))

        
    def testErrorTruncate(self):
        self.v.maxLength = 10
        self.v.truncate = 1
        self.assertEqual(self.v.validate(field, 'this is way too long'),
                         'this is way too long'[:10])


    def testErrorRequiredNotFound(self):
        # empty string
        field.isRequired = 1
        self.assertValidatorRaises(
            Errors.ValidationError, 'requiredNotFound',
            self.v.validate, (field, ''), {})

        # whitespace only
        self.assertValidatorRaises(
            Errors.ValidationError, 'requiredNotFound',
            self.v.validate, (field, '   '))


    def testIllegalValue(self):
        self.assertValidatorRaises(
            Errors.ValidationError, 'illegalValue',
            self.v.validate, (field, {}))

        
class EmailValidatorTestCase(ValidatorTestCase):
     
    def setUp(self):
        from Zope.App.Formulator.Validators import EmailValidator
        self.v = EmailValidator.EmailValidator()

        
    def testBasic(self):
        self.assertEqual(self.v.validate(field, 'foo@bar.com'),
                         'foo@bar.com')

        self.assertEqual(self.v.validate(field, 'm.faassen@vet.uu.nl'),
                         'm.faassen@vet.uu.nl')


    def testErrorNotEmail(self):
        # a few wrong email addresses should raise error
        self.assertValidatorRaises(
            Errors.ValidationError, 'notEmail',
            self.v.validate, (field, 'foo@bar.com.'))

        self.assertValidatorRaises(
            Errors.ValidationError, 'notEmail',
            self.v.validate, (field, '@bar.com'))

        
    def testErrorRequiredNotFound(self):
        field.isRequired = 1

        # empty string
        self.assertValidatorRaises(
            Errors.ValidationError, 'requiredNotFound',
            self.v.validate, (field, ''))


# skip PatternValidator for now

class BooleanValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        from Zope.App.Formulator.Validators import BooleanValidator
        self.v = BooleanValidator.BooleanValidator()
        

    def testBasic(self):
        self.assertEqual(self.v.validate(field, 't'), 1)
        self.assertEqual(self.v.validate(field, 1), 1)
        self.assertEqual(self.v.validate(field, 'f'), 0)
        self.assertEqual(self.v.validate(field, ''), 0)
        self.assertEqual(self.v.validate(field, 0), 0)
        self.assertEqual(self.v.validate(field, None), 0)



class IntegerValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        from Zope.App.Formulator.Validators import IntegerValidator
        self.v = IntegerValidator.IntegerValidator()


    def testBasic(self):
        self.assertEqual(self.v.validate(field, '15'), 15)
        self.assertEqual(self.v.validate(field, '0'), 0)
        self.assertEqual(self.v.validate(field, '-1'), -1)

        
    def testNoEntry(self):
        # result should be empty string if nothing entered
        field.isRequired = 0
        self.assertEqual(self.v.validate(field, ''), '')


    def testRanges(self):
        # first check whether everything that should be in range is
        # in range
        self.v.start = 0
        for i in range(0, 100):
            self.v.end = i+1
            self.assertEqual(self.v.validate(field, str(i)), i)

        # now check out of range errors
        self.v.start = 0
        self.v.end = 100
        self.assertValidatorRaises(
            Errors.ValidationError, 'integerOutOfRange',
            self.v.validate, (field, '100'))

        self.assertValidatorRaises(
            Errors.ValidationError, 'integerOutOfRange',
            self.v.validate, (field, '200'))

        self.assertValidatorRaises(
            Errors.ValidationError, 'integerOutOfRange',
            self.v.validate, (field, '-10'))

        # check some weird ranges
        self.v.start = 10
        self.v.end = 10
        self.assertValidatorRaises(
            Errors.ValidationError, 'integerOutOfRange',
            self.v.validate, (field, '10'))

        self.v.start = 0
        self.v.end = 0
        self.assertValidatorRaises(
            Errors.ValidationError, 'integerOutOfRange',
            self.v.validate, (field, '0'))

        self.v.start = 0
        self.v.end = -10
        self.assertValidatorRaises(
            Errors.ValidationError, 'integerOutOfRange',
            self.v.validate, (field, '-1'))

        
    def testErrorNotInteger(self):
        self.assertValidatorRaises(
            Errors.ValidationError, 'notInteger',
            self.v.validate, (field, 'foo'))

        self.assertValidatorRaises(
            Errors.ValidationError, 'notInteger',
            self.v.validate, (field, '1.0'))

        self.assertValidatorRaises(
            Errors.ValidationError, 'notInteger',
            self.v.validate, (field, '1e'))


    def testErrorRequiredNotFound(self):
        # empty string
        field.isRequired = 1
        self.assertValidatorRaises(
            Errors.ValidationError, 'requiredNotFound',
            self.v.validate, (field, ''), {})

        # whitespace only
        self.assertValidatorRaises(
            Errors.ValidationError, 'requiredNotFound',
            self.v.validate, (field, '   '))


class FloatValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        from Zope.App.Formulator.Validators import FloatValidator
        self.v = FloatValidator.FloatValidator()


    def testBasic(self):
        self.assertEqual(self.v.validate(field, '15.5'), 15.5)
        self.assertEqual(self.v.validate(field, '15.0'), 15.0)
        self.assertEqual(self.v.validate(field, '15'), 15.0)


    def testErrorNotFloat(self):
        self.assertValidatorRaises(
            Errors.ValidationError, 'notFloat',
            self.v.validate, (field, '1f'))



def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(StringValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(EmailValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(BooleanValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(IntegerValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(FloatValidatorTestCase, 'test'))
    
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
    
