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

$Id: testSecurityDirectives.py,v 1.2 2002/06/10 23:28:16 jim Exp $
"""

import unittest, sys, os

from Zope.Configuration.xmlconfig import xmlconfig
from StringIO import StringIO
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup
from Zope.Configuration.xmlconfig import ZopeXMLConfigurationError
from Zope.App.Security.PrincipalRegistry import principalRegistry
from Zope.App.Security.PermissionRegistry \
        import permissionRegistry as pregistry
from Zope.App.Security.RoleRegistry import roleRegistry as rregistry
from Zope.App.Security.RolePermissionManager \
        import rolePermissionManager as role_perm_mgr
from Zope.App.Security.PrincipalPermissionManager \
    import principalPermissionManager as principal_perm_mgr
from Zope.App.Security.PrincipalRoleManager \
    import principalRoleManager as principal_role_mgr
from Zope.App.Security.Settings import Allow, Deny, Unset, Remove, Assign


import Zope.App.Security
defs_path = os.path.join(
    os.path.split(Zope.App.Security.__file__)[0],
    'security-meta.zcml')

def configfile(s):
    return StringIO("""<zopeConfigure
      xmlns='http://namespaces.zope.org/zope'
      xmlns:security='http://namespaces.zope.org/security'>
      %s
      </zopeConfigure>
      """ % s)

class TestPrincipalDirective(CleanUp, unittest.TestCase):
    def setUp(self):
        xmlconfig(open(defs_path))

    def testRegister(self):
        f = configfile("""<security:principal id="1"
                             title="Sir Tim Peters"
                             description="Tim Peters"
                             login="tim" password="123" />
                          <security:principal id="2"
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
        xmlconfig(open(defs_path))

    def testRegister(self):
        f = configfile("""
 <security:permission
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
 <security:permission
     id="Can Do It"
     title="A Permissive Permission"
     description="This permission lets you do anything" />

 <security:permission
     id="Can Do It"
     title="A Permissive Permission"
     description="This permission lets you do anything" />
     """)

        #self.assertRaises(AlreadyRegisteredError, xmlconfig, f)
        self.assertRaises(ZopeXMLConfigurationError, xmlconfig, f)
        
class TestRoleDirective(CleanUp, unittest.TestCase):
    def setUp(self):
        xmlconfig(open(defs_path))

    def testRegister(self):
        f = configfile("""
 <security:role
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
 <security:role
     id="Everyperson"
     title="Tout le monde"
     description="The common man, woman, person, or thing" />

 <security:role
     id="Everyperson"
     title="Tout le monde"
     description="The common man, woman, person, or thing" />
     """)

        #self.assertRaises(AlreadyRegisteredError, xmlconfig, f)
        self.assertRaises(ZopeXMLConfigurationError, xmlconfig, f)

class TestRolePermission(CleanUp, unittest.TestCase):

    def setUp( self ):
        xmlconfig(open(defs_path))

    def testMap( self ):
        f = configfile("""
 <security:grantPermissionToRole
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
        xmlconfig(open(defs_path))

    def testMap( self ):
        f = configfile("""
 <security:grantPermissionToPrincipal
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
        xmlconfig(open(defs_path))

    def testMap( self ):
        f = configfile("""
 <security:assignRoleToPrincipal
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
