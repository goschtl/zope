##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""URI field tests
"""
from unittest import main, makeSuite

from six import u
from zope.schema import URI
from zope.schema.tests.test_field import FieldTestBase
from zope.schema.interfaces import RequiredMissing
from zope.schema.interfaces import InvalidURI, WrongType

class URITest(FieldTestBase):
    """Test the URI Field."""

    _Field_Factory = URI

    def testValidate(self):
        field = self._Field_Factory(
            title=u('Not required field'), description=u(''),
            readonly=False, required=False)
        field.validate(None)
        field.validate('http://www.example.com')
        self.assertRaises(WrongType, field.validate, 2)

    def testValidateRequired(self):
        field = self._Field_Factory(
            title=u('Required field'), description=u(''),
            readonly=False, required=True)
        field.validate('http://www.example.com')
        self.assertRaises(RequiredMissing, field.validate, None)

    def testFromUnicode(self):
        field = self._Field_Factory()
        # result is a native string
        self.assertEqual(
                field.fromUnicode(u("http://www.python.org/foo/bar")),
                'http://www.python.org/foo/bar')
        # leading/trailing whitespace is stripped
        self.assertEqual(
                field.fromUnicode(u("          http://www.python.org/foo/bar")),
                'http://www.python.org/foo/bar')
        self.assertEqual(
                field.fromUnicode(u("  \n http://www.python.org/foo/bar\n")),
                'http://www.python.org/foo/bar')
        # but not in the middle
        self.assertRaises(InvalidURI,
            field.fromUnicode,
            u("http://www.python.org/ foo/bar"))

def test_suite():
    suite = makeSuite(URITest)
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
