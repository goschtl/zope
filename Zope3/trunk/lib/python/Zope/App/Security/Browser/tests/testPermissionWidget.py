##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Permission field widget tests

$Id: testPermissionWidget.py,v 1.1 2002/12/21 19:57:30 stevea Exp $
"""

__metaclass__ = type

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp
from Zope.App.Security.PermissionField import PermissionField
from Zope.App.Security.Browser.PermissionWidget import SinglePermissionWidget
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.ComponentArchitecture.GlobalServiceManager \
     import serviceManager, defineService

from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.App.Security.Registries.PermissionRegistry import permissionRegistry
from Zope.ComponentArchitecture import getServiceManager
from Zope.App.Security.IPermissionService import IPermissionService

class TestPermissionWidget(PlacelessSetup, TestCase):

    def testPermissionWidget(self):
        defineService("Permissions", IPermissionService)
        serviceManager.provideService("Permissions", permissionRegistry)

        permissionRegistry.definePermission('read', 'Read', 'Read something')
        read_permission = permissionRegistry.getPermission('read')
        permissionRegistry.definePermission('reread', 'ReRead',
                                            'ReRead something')
        reread_permission = permissionRegistry.getPermission('reread')
        request = TestRequest()
        
        permissionField = PermissionField(__name__ = 'TestName',
                                          title = u"This is a test",
                                          required=False)
        
        widget = SinglePermissionWidget(permissionField, request)
        
        self.assertEqual(widget.getData(), None)
       
        out = (
        '<input type="text" name="field.TestName.search" value="">' 
        '<select name="field.TestName">' 
        '<option value="">---select permission---</option>'

        '<option value="'
        'Zope.Public'
        '">'
        'Zope.Public'
        '</option>'

        '<option value="'
        'read'
        '">'
        'read'
        '</option>'

        '<option value="'
        'reread'
        '">'
        'reread'
        '</option>'

        '</select>'
        )
        
        self.assertEqual(widget(), out)

        out = (
        '<input type="text" name="field.TestName.search" value="">' 
        '<select name="field.TestName">' 
        '<option value="">---select permission---</option>'

        '<option value="'
        'Zope.Public'
        '">'
        'Zope.Public'
        '</option>' 

        '<option value="'
        'read'
        '" selected>'
        'read'
        '</option>' 

        '<option value="'
        'reread'
        '">'
        'reread'
        '</option>'

        '</select>'
        )

        self.assertEqual(
                widget.render(read_permission),
                out)

        self.assertEqual(widget.getData(), None)

        widget = SinglePermissionWidget(permissionField, request)
        
        request.form["field.TestName"] = (
        'read'
        )
        self.assertEqual(widget.getData(), read_permission)

        self.assertEqual(widget(), out)
        
        request.form["field.TestName.search"] = 'read'

        out = (
        '<input type="text" name="field.TestName.search" value="read">' 
        '<select name="field.TestName">' 
        '<option value="">---select permission---</option>'

        '<option value="'
        'read'
        '" selected>'
        'read'
        '</option>' 

        '<option value="'
        'reread'
        '">'
        'reread'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

       
def test_suite():
    return TestSuite((makeSuite(TestPermissionWidget),))

if __name__=='__main__':
    main(defaultTest='test_suite')

