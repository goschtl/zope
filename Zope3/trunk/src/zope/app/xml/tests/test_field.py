##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
$Id: test_field.py,v 1.1 2003/04/09 09:31:53 faassen Exp $
"""
import unittest
from zope.app.xml.field import XML, NotWellFormedXML
from zope.schema.tests.test_field import FieldTestBase
from zope.schema import errornames

class XMLFieldTestCase(FieldTestBase):

    _Field_Factory = XML
    
    def testValidate(self):
        field = XML(title=u"XML field", description=u'',
                    readonly=False, required=False)
        field.validate('<doc/>')
        field.validate('<?xml version="1.0" ?><doc />')

        self.assertRaisesErrorNames(NotWellFormedXML, field.validate, 'foo')
        self.assertRaisesErrorNames(NotWellFormedXML, field.validate, '<doc>')
        self.assertRaisesErrorNames(NotWellFormedXML, field.validate,
                                    '<p></foo></p><foo>')
        # shouldn't accept this, as XML by default is encoded as UTF-8
        self.assertRaisesErrorNames(errornames.WrongType, field.validate,
                                    u'<doc></doc>')
        
    def testValidateRequired(self):
        field = XML(title=u"XML field", description=u'',
                    readonly=False, required=True)
        self.assertRaisesErrorNames(errornames.RequiredMissing,
                                    field.validate, None)
    
def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(XMLFieldTestCase)
        ])
