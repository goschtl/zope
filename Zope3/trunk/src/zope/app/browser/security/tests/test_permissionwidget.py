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

$Id: test_permissionwidget.py,v 1.4 2003/01/21 21:22:01 jim Exp $
"""

__metaclass__ = type

from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.cleanup import CleanUp
from zope.app.security.permission import PermissionField
from zope.app.browser.security.permissionwidget import SinglePermissionWidget
from zope.publisher.browser import TestRequest
from zope.component.service \
     import serviceManager, defineService

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.component import getServiceManager
from zope.app.interfaces.security import IPermissionService

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
        'read'
        '">'
        'read'
        '</option>'

        '<option value="'
        'reread'
        '">'
        'reread'
        '</option>'

        '<option value="'
        'zope.Public'
        '">'
        'zope.Public'
        '</option>'


        '</select>'
        )

        self.assertEqual(widget(), out)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
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

        '<option value="'
        'zope.Public'
        '">'
        'zope.Public'
        '</option>'

        '</select>'
        )

        self.assertEqual(
                widget.render(read_permission.getId()),
                out)

        self.assertEqual(widget.getData(), None)

        widget = SinglePermissionWidget(permissionField, request)

        request.form["field.TestName"] = (
        'read'
        )
        self.assertEqual(widget.getData(), read_permission.getId())

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
