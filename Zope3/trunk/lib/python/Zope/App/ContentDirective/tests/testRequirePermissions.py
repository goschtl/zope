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
""" Test handler for 'require' subdirective of 'content' directive """

import unittest
from cStringIO import StringIO

import Zope.Configuration
import Zope.App.Security
from Zope.App.Security import protectClass
from Zope.App.Security.Exceptions import UndefinedPermissionError
from Zope.Security.Checker import selectChecker
from Zope.Exceptions import Forbidden


# So we can use config parser to exercise protectClass stuff.
from Zope.Configuration.xmlconfig import xmlconfig, ZopeXMLConfigurationError
from Zope.Configuration.xmlconfig import XMLConfig

from TestModuleHookup import * # XXX I hate this!

from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

import Zope.App.ContentDirective

def defineDirectives():
    XMLConfig('metameta.zcml', Zope.Configuration)()
    XMLConfig('meta.zcml', Zope.App.ContentDirective)()
    XMLConfig('meta.zcml', Zope.App.Security)()
    xmlconfig(StringIO("""<zopeConfigure
        xmlns='http://namespaces.zope.org/zope' >
       <permission id="extravagant" title="extravagant" />
       <permission id="paltry" title="paltry" />
    </zopeConfigure>"""))

NOTSET = []

P1 = "extravagant"
P2 = "paltry"

class Test(CleanUp, unittest.TestCase):

    def setUp(self):
        defineDirectives()
        class B:
            def m1(self):
                return "m1"
            def m2(self):
                return "m2"
        class C(B):
            __implements__ = I
            def m3(self):
                return "m3"
            def m4(self):
                return "m4"
        TestModule.test_base = B
        TestModule.test_class = C
        TestModule.test_instance = C()
        self.assertState()

    def tearDown(self):
        CleanUp.tearDown(self)
        TestModule.test_class = None

    def assertState(self, m1P=NOTSET, m2P=NOTSET, m3P=NOTSET):
        "Verify that class, instance, and methods have expected permissions."

        from Zope.Security.Checker import selectChecker
        from Zope.Exceptions import Forbidden

        checker = selectChecker(TestModule.test_instance)
        self.assertEqual(checker.permission_id('m1'), (m1P or None))
        self.assertEqual(checker.permission_id('m2'), (m2P or None))
        self.assertEqual(checker.permission_id('m3'), (m3P or None))

    def assertDeclaration(self, declaration, **state):
        apply_declaration(template_bracket % declaration)
        self.assertState(**state)

    # "testSimple*" exercises tags that do NOT have children.  This mode
    # inherently sets the instances as well as the class attributes.

    def testSimpleMethodsPlural(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s" 
                                attributes="m1 m3"/>
                          </content>"""
                       % (PREFIX+"test_class", P1))
        self.assertDeclaration(declaration, m1P=P1, m3P=P1)

    def assertSetattrState(self, m1P=NOTSET, m2P=NOTSET, m3P=NOTSET):
        "Verify that class, instance, and methods have expected permissions."

        from Zope.Security.Checker import selectChecker
        from Zope.Exceptions import Forbidden

        checker = selectChecker(TestModule.test_instance)
        self.assertEqual(checker.setattr_permission_id('m1'), (m1P or None))
        self.assertEqual(checker.setattr_permission_id('m2'), (m2P or None))
        self.assertEqual(checker.setattr_permission_id('m3'), (m3P or None))

    def assertSetattrDeclaration(self, declaration, **state):
        self.assertSetattrState(**state)

    def test_set_attributes(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s" 
                                set_attributes="m1 m3"/>
                          </content>"""
                       % (PREFIX+"test_class", P1))
        apply_declaration(template_bracket % declaration)
        checker = selectChecker(TestModule.test_instance)
        self.assertEqual(checker.setattr_permission_id('m1'), P1)
        self.assertEqual(checker.setattr_permission_id('m2'), None)
        self.assertEqual(checker.setattr_permission_id('m3'), P1)

    def test_set_schema(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s" 
                                set_schema="%s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"S"))
        apply_declaration(template_bracket % declaration)
        checker = selectChecker(TestModule.test_instance)
        self.assertEqual(checker.setattr_permission_id('m1'), None)
        self.assertEqual(checker.setattr_permission_id('m2'), None)
        self.assertEqual(checker.setattr_permission_id('m3'), None)
        self.assertEqual(checker.setattr_permission_id('foo'), P1)
        self.assertEqual(checker.setattr_permission_id('bar'), P1)

    def testSimpleInterface(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s" 
                                interface="%s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"I"))
        # m1 and m2 are in the interface, so should be set, and m3 should not:
        self.assertDeclaration(declaration, m1P=P1, m2P=P1)

    # "testComposite*" exercises tags that DO have children.
    # "testComposite*TopPerm" exercises tags with permission in containing tag.
    # "testComposite*ElementPerm" exercises tags w/permission in children.

    def testCompositeNoPerm(self):
        # Establish rejection of declarations lacking a permission spec.
        declaration = ("""<content class="%s">
                            <require
                                attributes="m1"/>
                          </content>"""
                       % (PREFIX+"test_class"))
        self.assertRaises(ZopeXMLConfigurationError,
                          self.assertDeclaration,
                          declaration)



    def testCompositeMethodsPluralElementPerm(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                attributes="m1 m3"/>
                          </content>"""
                       % (PREFIX+"test_class", P1))
        self.assertDeclaration(declaration,
                               m1P=P1, m3P=P1)

    def testCompositeInterfaceTopPerm(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                interface="%s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"I"))
        self.assertDeclaration(declaration,
                               m1P=P1, m2P=P1)


    def testSubInterfaces(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                interface="%s"/>
                          </content>"""
                       % (PREFIX+"test_class", P1, PREFIX+"I2"))
        # m1 and m2 are in the interface, so should be set, and m3 should not:
        self.assertDeclaration(declaration, m1P=P1, m2P=P1)


    def testMimicOnly(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                attributes="m1 m2"/>
                          </content>
                          <content class="%s">
                            <require like_class="%s" />
                          </content>
                          """ % (PREFIX+"test_base", P1,
                PREFIX+"test_class", PREFIX+"test_base"))
        # m1 and m2 are in the interface, so should be set, and m3 should not:
        self.assertDeclaration(declaration,
                               m1P=P1, m2P=P1)
        

    def testMimicAsDefault(self):
        declaration = ("""<content class="%s">
                            <require
                                permission="%s"
                                attributes="m1 m2"/>
                          </content>
                          <content class="%s">
                            <require like_class="%s" />
                            <require
                                permission="%s"
                                attributes="m2 m3"/>
                          </content>
                          """ % (PREFIX+"test_base", P1,
                PREFIX+"test_class", PREFIX+"test_base", P2))

        # m1 and m2 are in the interface, so should be set, and m3 should not:
        self.assertDeclaration(declaration,
                               m1P=P1, m2P=P2, m3P=P2)


def apply_declaration(declaration):
    """Apply the xmlconfig machinery."""
    return xmlconfig(StringIO(declaration))

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
