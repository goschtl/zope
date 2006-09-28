##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

$Id$
"""
import os
import unittest
from zope import component, interface
import zope.security.interfaces
import zope.app.security.interfaces
from zope.app.testing import functional

import zc.security.interfaces
import zc.table.table
import zc.table.interfaces

class Principal:
    interface.implements(zope.security.interfaces.IPrincipal)

    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.groups = 'zope.Authenticated',
        

class Authentication:
    interface.implements(
        zope.app.security.interfaces.IAuthentication,
        zc.security.interfaces.ISimpleUserSearch,
        zc.security.interfaces.ISimpleGroupSearch,
        )

    def __init__(self):
        self.byId = dict(
            [(p.id, p) for p in [
                Principal('1', 'jim'),
                Principal('2', 'bob'),
                Principal('3', 'sally'),
                Principal('zope.manager', 'manager'),
                Principal('zope.Authenticated', 'Everybody'),
                ]
             ])
        
        self.byCred = {
            'jim:eek': self.byId['1'],
            }

    def searchUsers(self, filter, start, size):
        return '1', '2', '3'

    def searchGroups(self, filter, start, size):
        return 'zope.manager', 'zope.Authenticated'

    def authenticate(self, request):
        if request._auth:
            credentials = request._auth.split()[-1]
            return self.byCred.get(credentials.decode('base64'))

    def getPrincipal(self, id):
        return self.byId.get(id)

def formatterFactory(*args, **kw):
    return zc.table.table.FormFullFormatter(*args, **kw)
interface.directlyProvides(formatterFactory,
                           zc.table.interfaces.IFormatterFactory)

SharingLayer = functional.ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'SharingLayer')

def test_suite():
    suite = functional.FunctionalDocFileSuite('functional.txt')
    suite.layer = SharingLayer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

