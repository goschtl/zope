##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""Tests of PermissionRole
"""

__rcs_id__='$Id: testPermissionRole.py,v 1.1 2001/10/18 17:38:56 shane Exp $'
__version__='$Revision: 1.1 $'[11:-2]

import os, sys, unittest

from AccessControl.PermissionRole import PermissionRole
from Acquisition import Implicit, Explicit, aq_base

ViewPermission = 'View'
EditThingsPermission = 'Edit Things!'
DeletePermission = 'Delete'


class AppRoot(Explicit):
    _View_Permission = None
    _Edit_Things__Permission = ('Manager', 'Owner')
    # No default for delete permission.

class ImplicitContainer(Implicit):
    pass

class ExplicitContainer(Explicit):
    pass

class RestrictiveObject(Implicit):
    _View_Permission = ('Manager',)
    _Delete_Permission = ()  # Nobody

class PermissiveObject(Explicit):
    _Edit_Things__Permission = ['Anonymous']

class ZClassMethodish(Implicit):
    # Think of this as a method that should only be visible to users
    # who have the edit permission.
    _View_Permission = '_Edit_Things__Permission'
    _Edit_Things__Permission = ''
    _Delete_Permission = ''


def assertPRoles(ob, permission, expect):
    """
    Asserts that in the context of ob, the given permission maps to
    the given roles.
    """
    pr = PermissionRole(permission)
    roles = pr.__of__(ob)
    roles2 = aq_base(pr).__of__(ob)
    assert roles == roles2 or tuple(roles) == tuple(roles2), (
        'Different methods of checking roles computed unequal results')
    same = 0
    if roles is None or expect is None:
        if (roles is None or tuple(roles) == ('Anonymous',)) and (
            expect is None or tuple(expect) == ('Anonymous',)):
            same = 1
    else:
        got = {}
        for r in roles: got[r] = 1
        expected = {}
        for r in expect: expected[r] = 1
        if got == expected:  # Dict compare does the Right Thing.
            same = 1
    assert same, 'Expected roles: %s, got: %s' % (`expect`, `roles`)


class PermissionRoleTests (unittest.TestCase):

    def testRestrictive(self, explicit=0):
        app = AppRoot()
        if explicit:
            app.c = ExplicitContainer()
        else:
            app.c = ImplicitContainer()
        app.c.o = RestrictiveObject()
        o = app.c.o
        assertPRoles(o, ViewPermission,       ('Manager',))
        assertPRoles(o, EditThingsPermission, ('Manager','Owner',))
        assertPRoles(o, DeletePermission,     ())

    def testPermissive(self, explicit=0):
        app = AppRoot()
        if explicit:
            app.c = ExplicitContainer()
        else:
            app.c = ImplicitContainer()
        app.c.o = PermissiveObject()
        o = app.c.o
        assertPRoles(o, ViewPermission,       ('Anonymous',))
        assertPRoles(o, EditThingsPermission, ('Anonymous','Manager','Owner',))
        assertPRoles(o, DeletePermission,     ('Manager',))

    def testExplicit(self):
        self.testRestrictive(1)
        self.testPermissive(1)

    def testAppDefaults(self):
        o = AppRoot()
        assertPRoles(o, ViewPermission,       ('Anonymous',))
        assertPRoles(o, EditThingsPermission, ('Manager','Owner',))
        assertPRoles(o, DeletePermission,     ('Manager',))

    def testPermissionMapping(self):
        app = AppRoot()
        app.c = ImplicitContainer()
        app.c.o = ZClassMethodish()
        o = app.c.o
        assertPRoles(o, ViewPermission,       ('Manager','Owner',))
        assertPRoles(o, EditThingsPermission, ())
        assertPRoles(o, DeletePermission,     ())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PermissionRoleTests))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
