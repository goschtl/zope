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

$Id: testSecurityDirectives.py,v 1.4 2002/06/20 15:55:03 jim Exp $
"""

import unittest
from StringIO import StringIO

from Zope.Configuration.xmlconfig import ZopeXMLConfigurationError
from Zope.Configuration.xmlconfig import XMLConfig, xmlconfig

from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

import Zope.App.Security
from Zope.App.Security.Settings import Allow, Deny, Unset, Remove, Assign
from Zope.App.Security.Registries.PrincipalRegistry import principalRegistry
from Zope.App.Security.Registries.PermissionRegistry \
        import permissionRegistry as pregistry
from Zope.App.Security.Registries.RoleRegistry import roleRegistry as rregistry
from Zope.App.Security.Grants.Global.RolePermissionManager \
        import rolePermissionManager as role_perm_mgr
from Zope.App.Security.Grants.Global.PrincipalPermissionManager \
    import principalPermissionManager as principal_perm_mgr
from Zope.App.Security.Grants.Global.PrincipalRoleManager \
    import principalRoleManager as principal_role_mgr


def configfile(s):
    return StringIO("""<zopeConfigure
      xmlns='http://namespaces.zope.org/zope'>
      %s
      </zopeConfigure>
      """ % s)

class TestPrincipalDirective(CleanUp, unittest.TestCase):
    def setUp(self):
        XMLConfig('meta.zcml', Zope.App.Security)()

    def testRegister(self):
        f = configfile("""<principal id="1"
                             title="Sir Tim Peters"
                             description="Tim Peters"
                             login="tim" password="123" />
                          <principal id="2"
                             title="Sir Jim Fulton"
                             description="Jim Fulton"
                             login="jim" password="123" />""")
        xmlconfig(f)

        reg=principalRegistry
        
        p = reg.getPrincipal('1')
        self.assertEqual(p.getId(), '1')
        self.assertEqual(p.getTitle(), 'Sir Tim Peters')
        self.assertEqual(p.getDescription(), 'Tim Peters')
        p = reg.getPrincipal('2')
        self.assertEqual(p.getId(), '2')
        self.assertEqual(p.getTitle(), 'Sir Jim Fulton')
        self.assertEqual(p.getDescription(), 'Jim Fulton')

        self.assertEqual(len(reg.getPrincipals('')), 2)


class TestPermissionDirective(CleanUp, unittest.TestCase):
    def setUp(self):
        XMLConfig('meta.zcml', Zope.App.Security)()

    def testRegister(self):
        f = configfile("""
 <permission
     id="Can Do It"
     title="A Permissive Permission"
     description="This permission lets you do anything" />""")

        xmlconfig(f)

        perm = pregistry.getPermission("Can Do It")
        self.failUnless(perm.getId().endswith('Can Do It'))
        self.assertEqual(perm.getTitle(), 'A Permissive Permission')
        self.assertEqual(perm.getDescription(),
                         'This permission lets you do anything')

    def testDuplicationRegistration(self):
        f = configfile("""
 <permission
     id="Can Do It"
     title="A Permissive Permission"
     description="This permission lets you do anything" />

 <permission
     id="Can Do It"
     title="A Permissive Permission"
     description="This permission lets you do anything" />
     """)

        #self.assertRaises(AlreadyRegisteredError, xmlconfig, f)
        self.assertRaises(ZopeXMLConfigurationError, xmlconfig, f)
        
class TestRoleDirective(CleanUp, unittest.TestCase):
    def setUp(self):
        XMLConfig('meta.zcml', Zope.App.Security)()

    def testRegister(self):
        f = configfile("""
 <role
     id="Everyperson"
     title="Tout le monde"
     description="The common man, woman, person, or thing" />
     """)

        xmlconfig(f)

        role = rregistry.getRole("Everyperson")
        self.failUnless(role.getId().endswith('Everyperson'))
        self.assertEqual(role.getTitle(), 'Tout le monde')
        self.assertEqual(role.getDescription(),
                         'The common man, woman, person, or thing')
        
    def testDuplicationRegistration(self):
        f = configfile("""
 <role
     id="Everyperson"
     title="Tout le monde"
     description="The common man, woman, person, or thing" />

 <role
     id="Everyperson"
     title="Tout le monde"
     description="The common man, woman, person, or thing" />
     """)

        #self.assertRaises(AlreadyRegisteredError, xmlconfig, f)
        self.assertRaises(ZopeXMLConfigurationError, xmlconfig, f)

class TestRolePermission(CleanUp, unittest.TestCase):

    def setUp( self ):
        XMLConfig('meta.zcml', Zope.App.Security)()

    def testMap( self ):
        f = configfile("""
 <grant
     permission="Foo"
     role="Bar" />
     """)

        xmlconfig(f)

        roles = role_perm_mgr.getRolesForPermission("Foo")
        perms = role_perm_mgr.getPermissionsForRole("Bar")

        self.assertEqual(len( roles ), 1)
        self.failUnless(("Bar",Allow) in roles)

        self.assertEqual(len( perms ), 1)
        self.failUnless(("Foo",Allow) in perms)

class TestPrincipalPermission(CleanUp, unittest.TestCase):

    def setUp( self ):
        XMLConfig('meta.zcml', Zope.App.Security)()

    def testMap( self ):
        f = configfile("""
 <grant
     permission="Foo"
     principal="Bar" />
     """)

        xmlconfig(f)

        principals = principal_perm_mgr.getPrincipalsForPermission("Foo")
        perms = principal_perm_mgr.getPermissionsForPrincipal("Bar")

        self.assertEqual(len( principals ), 1)
        self.failUnless(("Bar", Allow) in principals)

        self.assertEqual(len( perms ), 1)
        self.failUnless(("Foo", Allow) in perms)

class TestPrincipalRole(CleanUp, unittest.TestCase):

    def setUp( self ):
        XMLConfig('meta.zcml', Zope.App.Security)()

    def testMap( self ):
        f = configfile("""
 <grant
     role="Foo"
     principal="Bar" />
     """)

        xmlconfig(f)

        principals = principal_role_mgr.getPrincipalsForRole("Foo")
        roles = principal_role_mgr.getRolesForPrincipal("Bar")

        self.assertEqual(len( principals ), 1)
        self.failUnless(("Bar",Assign) in principals)

        self.assertEqual(len( roles ), 1)
        self.failUnless(("Foo",Assign) in roles)

def test_suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestPrincipalDirective))
    suite.addTest(loader.loadTestsFromTestCase(TestPermissionDirective))
    suite.addTest(loader.loadTestsFromTestCase(TestRoleDirective))
    suite.addTest(loader.loadTestsFromTestCase(TestRolePermission))
    suite.addTest(loader.loadTestsFromTestCase(TestPrincipalPermission))
    suite.addTest(loader.loadTestsFromTestCase(TestPrincipalRole))
    return suite


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
