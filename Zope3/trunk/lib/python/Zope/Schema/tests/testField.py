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
$Id: testField.py,v 1.5 2002/12/05 13:27:07 dannu Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Schema import Field, Text, IField, ErrorNames, Int
from Zope.Schema.Exceptions import StopValidation, ValidationError

class FieldTestBase(TestCase):

    def assertRaisesErrorNames(self, error_name, f, *args, **kw):
        try:
            f(*args, **kw)
        except ValidationError, e:
            self.assertEquals(error_name, e[0])
            return
        self.fail('Expected ValidationError')

    def test_bind(self):
        field = self._Field_Factory(
            __name__ = 'x',
            title=u'Not required field', description=u'',
            readonly=False, required=False)

        class C(object):
            x=None

        c = C()
        field2 = field.bind(c)

        self.assertEqual(field2.context, c)
        for n in ('__class__', '__name__', 'title', 'description',
                  'readonly', 'required'):
            self.assertEquals(getattr(field2, n), getattr(field, n), n)

    def testValidate(self):
        field = self._Field_Factory(
            title=u'Not required field', description=u'',
            readonly=False, required=False)
        field.validate(None)
        field.validate('foo')
        field.validate(1)
        field.validate(0)
        field.validate('')
    
    def testValidateRequired(self):
        field = self._Field_Factory(
            title=u'Required field', description=u'',
            readonly=False, required=True)
        field.validate('foo')
        field.validate(1)
        field.validate(0)
        field.validate('')
            
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

class FieldTest(FieldTestBase):
    """Test generic Field."""

    
    _Field_Factory = Field


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

    def testConstraint(self):
        def isodd(x):
            return x % 2 == 1

        i = Int(title=u'my constrained integer',
                constraint=isodd)

        i.validate(11)
        self.assertRaisesErrorNames(ErrorNames.ConstraintNotSatisfied,
                                    i.validate, 10)
        
                           
class FieldDefaultBehaviour(TestCase):
    def test_required_defaults_to_true(self):
        class MyField(Field):
            pass
        field = MyField(title=u'my')
        self.assert_(field.required)

def test_suite():
    return TestSuite(   (
            makeSuite(FieldTest),
            makeSuite(FieldDefaultBehaviour)
    ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
