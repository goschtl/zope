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
This test suite tests all **registered** fields. The other fields are there
for historical reasons and may or may not make it into Zope 3.

$Id: testGenericFields.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

import unittest
from Zope.App.Formulator.Fields.Generic.DateTimeField import DateTimeField
from Zope.App.Formulator.Fields.Generic.EmailField import EmailField
from Zope.App.Formulator.Fields.Generic.FileField import FileField
from Zope.App.Formulator.Fields.Generic.FloatField import FloatField
from Zope.App.Formulator.Fields.Generic.IntegerField import IntegerField
from Zope.App.Formulator.Fields.Generic.ListField import ListField
from Zope.App.Formulator.Fields.Generic.PasswordField import PasswordField
from Zope.App.Formulator.Fields.Generic.PatternField import PatternField
from Zope.App.Formulator.Fields.Generic.StringField import StringField


class Test( unittest.TestCase ):


    def testDateTimeField(self):
        field = DateTimeField(id='some',
                              title='Something',
                              description='This is some field.',
                              required=1,
                              default='1970/01/01 00:00:00.00 GMT')

        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, '1970/01/01 00:00:00.00 GMT')


    def testEmailField(self):
        field = EmailField(id='some',
                           title='Something',
                           description='This is some field.',
                           required=1,
                           default='zope3@zope.org')

        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, 'zope3@zope.org')


    def testFileField(self):
        field = FileField(id='some',
                          title='Something',
                          description='This is some field.',
                          required=1,
                          default='')

        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, '')


    def testFloatField(self):
        field = FloatField(id='some',
                          title='Something',
                          description='This is some field.',
                          required=1,
                          default=3.3)

        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, 3.3)


    def testIntegerField(self):
        field = IntegerField(id='some',
                             title='Something',
                             description='This is some field.',
                             required=1,
                             default=3)

        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, 3)


    def testListField(self):
        field = ListField(id='some',
                          title='Something',
                          description='This is some field.',
                          required=1,
                          default=[0, 1, 2])

        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, [0, 1, 2])


    def testPasswordField(self):
        field = PasswordField(id='some',
                              title='Something',
                              description='This is some field.',
                              required=1,
                              default='pass')

        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, 'pass')


    def testPatternField(self):
        field = PatternField(id='some',
                              title='Something',
                              description='This is some field.',
                              required=1,
                              default='eee.dd')

        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, 'eee.dd')


    def testStringField(self):
        field = StringField(id='some',
                            title='Something',
                            description='This is some field.',
                            required=1,
                            default='Empty')

        self.assertEqual(field.context, None)
        self.assertEqual(field.id, 'some')
        self.assertEqual(field.title, 'Something')
        self.assertEqual(field.description, 'This is some field.')
        self.assertEqual(field.required, 1)
        self.assertEqual(field.default, 'Empty')



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )


if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
