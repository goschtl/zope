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
$Id: testField.py,v 1.2 2002/09/11 22:06:41 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Schema import Field, Text, IField, ErrorNames
from Zope.Schema.Exceptions import StopValidation, ValidationError

class FieldTestBase(TestCase):

    def assertRaisesErrorNames(self, error_name, f, *args, **kw):
        try:
            f(*args, **kw)
        except ValidationError, e:
            self.assertEquals(error_name, e[0])
            return
        self.fail('Expected ValidationError')


class FieldTest(FieldTestBase):
    """Test generic Field."""

    def testValidate(self):
        field = Field(title=u'Not required field', description=u'',
                      readonly=0, required=0)
        field.validate(None)
        field.validate('foo')
        field.validate(1)
        field.validate(0)
        field.validate('')
    
    def testValidateRequired(self):
        field = Field(title=u'Required field', description=u'',
                      readonly=0, required=1)
        field.validate('foo')
        field.validate(1)
        field.validate(0)
        field.validate('')
            
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testSillyDefault(self):
        
        self.assertRaises(ValidationError, Text, default="")

    def test__doc__(self):
        field = Text(title=u"test fiield",
                     description=(
                         u"To make sure that\n"
                         u"doc strings are working correctly\n"
                         )
                     )
        self.assertEqual(
            field.__doc__,
            u"test fiield\n\n"
            u"To make sure that\n"
            u"doc strings are working correctly\n"
            )

    def testOrdering(self):

        from Interface import Interface

        class S1(Interface):
            a = Text()
            b = Text()

        self.failUnless(S1['a'].order < S1['b'].order)

        class S2(Interface):
            b = Text()
            a = Text()

        self.failUnless(S2['a'].order > S2['b'].order)
                           
        

def test_suite():
    return makeSuite(FieldTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
