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

$Id: test_directives.py,v 1.3 2002/12/31 03:35:07 jim Exp $
"""

import unittest
import sys
import os
from StringIO import StringIO

from zope.configuration.xmlconfig import xmlconfig, XMLConfig
from zope.configuration.xmlconfig import ZopeXMLConfigurationError
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.security.management import newSecurityManager, system_user
import zope.configuration
import zope.app.security
import zope.app.contentdirective
from zope.app.security.exceptions import UndefinedPermissionError

# explicitly import ExampleClass and IExample using full paths
# so that they are the same objects as resolve will get.
from zope.app.contentdirective.tests.exampleclass import ExampleClass, IExample


def configfile(s):
    return StringIO("""<zopeConfigure
      xmlns='http://namespaces.zope.org/zope'>
      %s
      </zopeConfigure>
      """ % s)

class TestContentDirective(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        PlacelessSetup.setUp(self)
        newSecurityManager(system_user)
        XMLConfig('metameta.zcml', zope.configuration)()
        XMLConfig('meta.zcml', zope.app.contentdirective)()
        XMLConfig('meta.zcml', zope.app.security)()

        try:
            del ExampleClass.__implements__
        except AttributeError:
            pass

    def testEmptyDirective(self):
        f = configfile("""
<content class="zope.app.contentdirective.tests.exampleclass.ExampleClass">
</content>
                       """)
        xmlconfig(f)


    def testImplements(self):
        f = configfile("""
<content class="zope.app.contentdirective.tests.exampleclass.ExampleClass">
  <implements interface="zope.app.contentdirective.tests.exampleclass.IExample" />
</content>
                       """)
        xmlconfig(f)
        self.failUnless(IExample.isImplementedByInstancesOf(ExampleClass))


    def testRequire(self):
        f = configfile("""
<permission id="zope.View" title="Zope view permission" />
<content class="zope.app.contentdirective.tests.exampleclass.ExampleClass">
    <require permission="zope.View"
                      attributes="anAttribute anotherAttribute" />
</content>
                       """)
        xmlconfig(f)

    def testAllow(self):
        f = configfile("""
<content class="zope.app.contentdirective.tests.exampleclass.ExampleClass">
    <allow attributes="anAttribute anotherAttribute" />
</content>
                       """)
        xmlconfig(f)

    def testMimic(self):
        f = configfile("""
<content class="zope.app.contentdirective.tests.exampleclass.ExampleClass">
    <require like_class="zope.app.contentdirective.tests.exampleclass.ExampleClass" />
</content>
                       """)
        xmlconfig(f)


class TestFactorySubdirective(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        PlacelessSetup.setUp(self)
        newSecurityManager(system_user)
        XMLConfig('metameta.zcml', zope.configuration)()
        XMLConfig('meta.zcml', zope.app.contentdirective)()
        XMLConfig('meta.zcml', zope.app.security)()

    def testFactory(self):
        f = configfile("""
<permission id="zope.Foo" title="Zope Foo Permission" />

<content class="zope.app.contentdirective.tests.exampleclass.ExampleClass">
    <factory
      id="Example"
      permission="zope.Foo"
      title="Example content"
      description="Example description"
    />
</content>
                       """)
        xmlconfig(f)


    def testFactoryUndefinedPermission(self):

        f = configfile("""
<permission id="zope.Foo" title="Zope Foo Permission" />

<content class="zope.app.contentdirective.tests.exampleclass.ExampleClass">
    <factory
      id="Example"
      permission="UndefinedPermission"
      title="Example content"
      description="Example description"
    />
</content>
            """)
        self.assertRaises(UndefinedPermissionError, xmlconfig, f,
                          testing=1)


def test_suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestContentDirective))
    suite.addTest(loader.loadTestsFromTestCase(TestFactorySubdirective))
    return suite


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
