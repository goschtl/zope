#############################################################################
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
"""Form Directives Tests

$Id: test_directives.py,v 1.2 2004/03/17 17:37:06 philikon Exp $
"""
import os
import unittest
from cStringIO import StringIO

from zope.app import zapi
from zope.interface import Interface, implements

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.component import getDefaultViewName, getResource
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.proxy import ProxyFactory

from zope.component.exceptions import ComponentLookupError

from zope.publisher.browser import TestRequest

import zope.app.publisher.browser

from zope.schema import TextLine

tests_path = os.path.join(
    os.path.split(zope.app.publisher.browser.__file__)[0],
    'tests')

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   xmlns:browser='http://namespaces.zope.org/browser'
   i18n_domain='zope'>
   %s
   </configure>"""


request = TestRequest()

class Schema(Interface):

    text = TextLine(
        title=u'Text',
        description=u'Nice text',
        required=False)

class IC(Schema): pass

class Ob:
    implements(IC)

ob = Ob()


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        XMLConfig('meta.zcml', zope.app.component)()
        XMLConfig('meta.zcml', zope.app.form.browser)()
        XMLConfig('meta.zcml', zope.app.publisher.browser)()

        from zope.app.tests import ztapi
        from zope.app.traversing.adapters import DefaultTraversable
        from zope.app.traversing.interfaces import ITraversable

        ztapi.provideAdapter(None, ITraversable, DefaultTraversable)

        ps =  zapi.getService(None, zapi.servicenames.Presentation)
        ps.defineUsage("objectview")
        ps.defineUsage("overridden")
        
    def testEditForm(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)
        xmlconfig(StringIO(template % ("""
          <view
              type="zope.publisher.interfaces.browser.IBrowserRequest"
              for="zope.schema.interfaces.ITextLine"
              provides="zope.app.form.interfaces.IInputWidget"
              factory="zope.app.form.browser.TextWidget"
              permission="zope.Public"
              />

          <browser:editform
              for="zope.app.form.browser.tests.test_directives.IC"
              schema="zope.app.form.browser.tests.test_directives.Schema"
              name="edit.html"
              label="Edit a ZPT page"
              fields="text"
              permission="zope.Public" />
            """)))

        v = zapi.queryView(ob, 'edit.html', request)
        # expect component lookup as standard macros are not configured
        self.assertRaises(ComponentLookupError, v)


    def testEditFormWithMenu(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)
        xmlconfig(StringIO(template % ("""
          <browser:menu id="test_menu" title="Test menu" usage="objectview"/>
          <view
              type="zope.publisher.interfaces.browser.IBrowserRequest"
              for="zope.schema.interfaces.ITextLine"
              provides="zope.app.form.interfaces.IInputWidget"
              factory="zope.app.form.browser.TextWidget"
              permission="zope.Public"
              />
          <browser:editform
              for="zope.app.form.browser.tests.test_directives.IC"
              schema="zope.app.form.browser.tests.test_directives.Schema"
              name="edit.html"
              label="Edit a ZPT page"
              fields="text"
              permission="zope.Public"
              menu="test_menu"
              title="Test View"
              />
            """)))

        v = zapi.queryView(ob, 'edit.html', request)
        self.assertEqual(v.usage, 'objectview')
        # expect component lookup as standard macros are not configured
        self.assertRaises(ComponentLookupError, v)

    def testEditFormWithUsage(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)
        xmlconfig(StringIO(template % ("""
          <view
              type="zope.publisher.interfaces.browser.IBrowserRequest"
              for="zope.schema.interfaces.ITextLine"
              provides="zope.app.form.interfaces.IInputWidget"
              factory="zope.app.form.browser.TextWidget"
              permission="zope.Public"
              />
          <browser:editform
              for="zope.app.form.browser.tests.test_directives.IC"
              schema="zope.app.form.browser.tests.test_directives.Schema"
              name="edit.html"
              label="Edit a ZPT page"
              fields="text"
              permission="zope.Public"
              usage="objectview"
              />
            """)))

        v = zapi.queryView(ob, 'edit.html', request)
        self.assertEqual(v.usage, 'objectview')
        # expect component lookup as standard macros are not configured
        self.assertRaises(ComponentLookupError, v)


    def testEditFormWithMenuAndUsage(self):
        self.assertEqual(zapi.queryView(ob, 'test', request),
                         None)
        xmlconfig(StringIO(template % ("""
          <browser:menu id="test_menu" title="Test menu" usage="overridden"/>
          <view
              type="zope.publisher.interfaces.browser.IBrowserRequest"
              for="zope.schema.interfaces.ITextLine"
              provides="zope.app.form.interfaces.IInputWidget"
              factory="zope.app.form.browser.TextWidget"
              permission="zope.Public"
              />
          <browser:editform
              for="zope.app.form.browser.tests.test_directives.IC"
              schema="zope.app.form.browser.tests.test_directives.Schema"
              name="edit.html"
              label="Edit a ZPT page"
              fields="text"
              permission="zope.Public"
              menu="test_menu"
              title="Test View"
              usage="objectview"        
              />
            """)))

        v = zapi.queryView(ob, 'edit.html', request)
        self.assertEqual(v.usage, 'objectview')
        # expect component lookup as standard macros are not configured
        self.assertRaises(ComponentLookupError, v)

# XXX Tests for AddFormDirective are missing

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
