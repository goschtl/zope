#!/usr/bin/env python2.1

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

# $Id: regressionSecurity.py,v 1.2 2001/10/18 14:30:51 andreasjung Exp $

import os, sys, unittest

import Zope
from OFS.Folder import Folder
from OFS.SimpleItem  import SimpleItem
from AccessControl import ClassSecurityInfo,getSecurityManager
from AccessControl.User import nobody
import Globals

import SecurityBase

# let's define some permissions first

MAGIC_PERMISSION1 = 'Magic Permission 1'
MAGIC_PERMISSION2 = 'Magic Permission 2'


##############################################################################
# TestObject class
##############################################################################

class TestObject(SimpleItem):
    """ test object """

    security = ClassSecurityInfo()
    __allow_access_to_unprotected_subobjects__ = 0

    public_attr     = 1
    _protected_attr = 2

    def __init__(self,id):
        self.id = id

    security.declarePrivate("private_func")
    def private_func(self):
        """ private func """
        return "i am private"


    def manage_func(self):
        """ should be protected by manager role """
        return "i am your manager function"


    security.declareProtected(MAGIC_PERMISSION2,"manage_func2")
    def manage_func2(self):
        """ should be protected by manager role """
        return "i am your manager function2"


    security.declareProtected(MAGIC_PERMISSION1,"protected_func")
    def protected_func(self):
        """ proteced func """
        return "i am protected "


    security.declarePublic("public_func")
    def public_func(self):
        """ public func """
        return "i am public"

    security.setPermissionDefault(MAGIC_PERMISSION1, ("Manager","Owner"))
    security.setPermissionDefault(MAGIC_PERMISSION2, ("TestRole",))

Globals.InitializeClass(TestObject)


##############################################################################
# Testfolder class
##############################################################################

class TestFolder(Folder):
    """ test class """

    def __init__(self,id):
        self.id = id
            

    def getId(self): return self.id 

    meta_type = 'TestFolder'

    security = ClassSecurityInfo()

Globals.InitializeClass(TestFolder)


##############################################################################
# User Class
##############################################################################

class User:

    def __init__(self,username,password,roles):
        self.username = username
        self.password = password
        self.roles    = roles

    def auth(self):
        return "%s:%s" % (self.username,self.password)


    def __str__(self):
        return "User(%s:%s:%s)" % (self.username,self.password,self.roles)

    __repr__ = __str__


USERS = (
    User('user1','123',[]),
    User('user2','123',[]),
    User('owner','123',('Owner',)),
    User('manager','123',('Manager',))
)

def getAuth(username):

    for user in USERS:
        if user.username==username:
            return "%s:%s" % (user.username,user.password)

    raise KeyError,"no such username: %" % username


class AVeryBasicSecurityTest(SecurityBase.SecurityBase):

    ################################################################
    # set up the test hierachy of objects
    ################################################################

    def setUp(self):
        """ my setup """

        self.root = Zope.app()
        acl = self.root.acl_users

        for user in USERS:
            try: acl._delUsers( user.username )
            except: pass
   
        for user in USERS:
            acl._addUser(user.username,user.password,user.password,
                            user.roles, [])

        get_transaction().commit()

        # try to remove old crap

        if 'test' in self.root.objectIds():
            self.root._delObject('test') 

        # setup Folder hierarchy

        test     = TestFolder('test')
        f1       = TestFolder('f1')
        f2       = TestFolder('f2')
        f3       = TestFolder('f3')
        obj      = TestObject('obj3')
        anonobj  = TestObject('anonobj')
        anonobj.__roles__ = ('Anonymous',)

        self.root._setObject('test',test)
        self.root.test._setObject('f1',f1)
        self.root.test._setObject('f2',f2)
        self.root.test.f1._setObject('anonobj',anonobj)
        self.root.test.f2._setObject('f3',f3)
        self.root.test.f2.f3._setObject('obj3',obj)
        
        get_transaction().commit()


    def testNobody(self):
        """ check permissions for nobody user """

        self._checkPermission(nobody,'test.f1',   'View',1) 
        self._checkPermission(nobody,'test.f2',   'View',1) 
        self._checkPermission(nobody,'test.f2.f3','View',1) 
        self._checkPermission(nobody,'test.f1',   MAGIC_PERMISSION1, None) 
        self._checkPermission(nobody,'test.f2',   MAGIC_PERMISSION1, None) 
        self._checkPermission(nobody,'test.f2.f3',MAGIC_PERMISSION1, None) 


    def testPermissionAccess(self):
        """ check permission based access """

        self._checkRoles('test.f2.f3.obj3.public_func',     ())    
        self._checkRoles('test.f2.f3.obj3.protected_func',  ('Manager','Owner'))    
        self._checkRoles('test.f2.f3.obj3.manage_func',     ('Manager',))    
        self._checkRoles('test.f2.f3.obj3.private_func',    ())    


    def testZPublisherAccess(self):
        """ test access through ZPublisher """

        _r = [
               ('/test/f1/',                        None,    200),
               ('/test/f2',                         None,    200),
               ('/test/f2/f3',                      None,    200),
               ('/test/f2/f3/obj3/public_func',     None,    200),
               ('/test/f2/f3/obj3/protected_func',  None,    401),
               ('/test/f2/f3/obj3/manage_func',     None,    401),
               ('/test/f2/f3/obj3/private_func',    None,    401),

               ('/test/f1/',                        getAuth('manager'),    200),
               ('/test/f2',                         getAuth('manager'),    200),
               ('/test/f2/f3',                      getAuth('manager'),    200),
               ('/test/f2/f3/obj3/public_func',     getAuth('manager'),    200),
               ('/test/f2/f3/obj3/protected_func',  getAuth('manager'),    200),
               ('/test/f2/f3/obj3/manage_func',     getAuth('manager'),    200),
               ('/test/f2/f3/obj3/private_func',    getAuth('manager'),    401),

               ('/test/f1/',                        getAuth('owner'),    200),
               ('/test/f2',                         getAuth('owner'),    200),
               ('/test/f2/f3',                      getAuth('owner'),    200),
               ('/test/f2/f3/obj3/public_func',     getAuth('owner'),    200),
               ('/test/f2/f3/obj3/protected_func',  getAuth('owner'),    200),
               ('/test/f2/f3/obj3/manage_func',     getAuth('owner'),    401),
               ('/test/f2/f3/obj3/private_func',    getAuth('owner'),    401),

              ]

        for path,auth,expected in _r:
            if auth:
                res = self._checkRequest(path,u=auth,expected=expected)
            else:
                res = self._checkRequest(path,expected=expected)


def test_suite():
    return unittest.makeSuite(AVeryBasicSecurityTest)

        
def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
