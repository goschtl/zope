##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Test object widget

$Id$
"""
import unittest
from zope.component.testing import PlacelessSetup
from zope.configuration.xmlconfig import XMLConfig
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.schema import Object, TextLine
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser.tests import support

class ITestContact(Interface):
    name = TextLine()
    email = TextLine()

class TestContact(object):
    implements(ITestContact)

class Test(PlacelessSetup, unittest.TestCase, support.VerifyResults):

    def setUp(self):
        PlacelessSetup.setUp(self)
        import zope.app.form
        XMLConfig('ftesting.zcml', zope.app.form)()
        self.field = Object(ITestContact, __name__=u'foo')

    def test_new(self):
        request = TestRequest()
        widget = ObjectWidget(self.field, request, TestContact)
        self.assertEquals(int(widget.hasInput()), 0)
        check_list = (
            'input', 'name="field.foo.name"',
            'input', 'name="field.foo.email"'
        )
        self.verifyResult(widget(), check_list)

    def test_edit(self):
        request = TestRequest(form={
            'field.foo.name': u'fred',
            'field.foo.email': u'fred@fred.com'
            })
        widget = ObjectWidget(self.field, request, TestContact)
        self.assertEquals(int(widget.hasInput()), 1)
        o = widget.getInputValue()
        self.assertEquals(hasattr(o, 'name'), 1)
        self.assertEquals(o.name, u'fred')
        self.assertEquals(o.email, u'fred@fred.com')
        check_list = (
            'input', 'name="field.foo.name"', 'value="fred"',
            'input', 'name="field.foo.email"', 'value="fred@fred.com"',
        )
        self.verifyResult(widget(), check_list)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
