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
$Id: test_schema.py,v 1.3 2003/01/09 14:13:20 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.schema.interfaces import StopValidation, ValidationError
from zope.interface import Interface
from zope.schema import Bytes
from zope.schema.errornames import RequiredMissing
from zope.schema import getFields, getFieldsInOrder

class ISchemaTest(Interface):
    title = Bytes(
        title=u"Title",
        description=u"Title",
        default="",
        required=True)

    description = Bytes(
        title=u"Description",
        description=u"Description",
        default="",
        required=True)

    spam = Bytes(
        title=u"Spam",
        description=u"Spam",
        default="",
        required=True)

class SchemaTest(TestCase):

    def test_getFields(self):
        fields = getFields(ISchemaTest)

        self.assert_(fields.has_key('title'))
        self.assert_(fields.has_key('description'))
        self.assert_(fields.has_key('spam'))

        # test whether getName() has the right value
        for key, value in fields.iteritems():
            self.assertEquals(key, value.getName())

    def test_getFieldsInOrder(self):
        fields = getFieldsInOrder(ISchemaTest)
        field_names = [name for name, field in fields]
        self.assertEquals(field_names, ['title', 'description', 'spam'])
        for key, value in fields:
            self.assertEquals(key, value.getName())

def test_suite():
    return makeSuite(SchemaTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
