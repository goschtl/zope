##############################################################################
#
# Copyright (c) 2001-2007 Zope Corporation and Contributors.
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
from zope.testing import doctest
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.schema import Object, TextLine
import zope.security.checker
import zope.location.location

from zope.app.form.browser import ObjectWidget
from zope.app.testing.functional import BrowserTestCase
from zope.app.form.browser.tests import support
from zope.app.form.testing import AppFormLayer


class ITestContact(Interface):
    name = TextLine()
    email = TextLine()


class TestContact(object):
    implements(ITestContact)


class Test(BrowserTestCase, support.VerifyResults):

    def setUp(self):
        BrowserTestCase.setUp(self)
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

    def test_location(self):
        # Objects that are managed through an object field are automatically.
        # This is done to make objects created through sub-forms compatible
        # with the Zope security policy which bases it's decisions on the
        # location of objects.
        context = zope.location.location.Location()
        value = TestContact()
        field = zope.schema.Object(Interface,
                                   __name__='test_object')
        field.set(context, value)

        self.assertEquals(context, context.test_object.__parent__)
        self.assertEquals('test_object', context.test_object.__name__)

    def test_location_wrapper(self):
        # Objects that do not implement the ILocation interface will be
        # wrapped with a location proxy.
        class Dummy(object):
            pass
        context = Dummy()
        value = TestContact()
        field = zope.schema.Object(Interface,
                                   __name__='test_object')
        field.set(context, value)

        self.failIf(zope.location.interfaces.ILocation.providedBy(value))
        self.failUnless(zope.location.interfaces.ILocation.providedBy(
            context.test_object))
        self.assertEquals(context, context.test_object.__parent__)
        self.assertEquals('test_object', context.test_object.__name__)


def test_suite():
    suite = unittest.TestSuite()
    Test.layer = AppFormLayer
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
