##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: test_objectwidget.py 26551 2004-07-15 07:06:37Z srichter $
"""
import unittest, doctest

from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest
from zope.schema import Schema, TextLine
from zope.component.interfaces import IFactory
from zope.component.factory import Factory
from zope.app import zapi
from zope.app.form.browser import SchemaWidget
from zope.app.tests.functional import BrowserTestCase
from zope.app.form.browser.tests import support
from zope.app.tests import ztapi


class ITestChild(Interface):
    name = TextLine()
    
class TestChild(object):
    implements(ITestChild)
    
    def __init__(self, name=''):
        self.name = name


class Test(BrowserTestCase, support.VerifyResults):
    
    def setUp(self):
        BrowserTestCase.setUp(self)
        util = zapi.getGlobalServices().getService(zapi.servicenames.Adapters)
        ztapi.provideAdapter(None, ITestChild, TestChild)
        self.field = Schema(ITestChild)

    def test_new(self):
        request = TestRequest()
        widget = SchemaWidget(self.field, request)
        self.assertEquals(int(widget.hasInput()), 0)
        check_list = (
            'input', 'name="field.name"'
        )
        self.verifyResult(widget(), check_list)

    def test_edit(self):
        request = TestRequest(form={
            'field.name': u'fred'
            })
        widget = SchemaWidget(self.field, request)
        self.assertEquals(int(widget.hasInput()), 1)
        o = widget.getInputValue()
        self.assertEquals(hasattr(o, 'name'), 1)
        self.assertEquals(o.name, u'fred')
        check_list = (
            'input', 'name="field.name"', 'value="fred"',
        )
        self.verifyResult(widget(), check_list)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')



