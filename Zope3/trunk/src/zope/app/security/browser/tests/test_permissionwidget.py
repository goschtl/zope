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

$Id: test_permissionwidget.py,v 1.2 2004/03/13 21:37:29 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.security.checker import CheckerPublic
from zope.app.security.interfaces import IPermission
from zope.app.security.permission import Permission, PermissionField
from zope.app.security.browser.permissionwidget import SinglePermissionWidget
from zope.publisher.browser import TestRequest

from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.form.interfaces import WidgetInputError

class TestPermissionWidget(PlacelessSetup, TestCase):

    def testPermissionWidget(self):
        read_permission = Permission('read', 'Read', 'Read something')
        ztapi.provideUtility(IPermission, read_permission, 'read')

        reread_permission = Permission('reread', 'ReRead', 'ReRead something')
        ztapi.provideUtility(IPermission, reread_permission, 'reread')

        request = TestRequest()

        permissionField = PermissionField(__name__ = 'TestName',
                                          title = u"This is a test",
                                          required=False)

        widget = SinglePermissionWidget(permissionField, request)

        self.assertRaises(WidgetInputError, widget.getInputValue)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select permission---</option>'
        '<option value="read">read</option>'
        '<option value="reread">reread</option>'
        '<option value="zope.Public">zope.Public</option>'
        '</select>'
        )

        self.assertEqual(widget(), out)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select permission---</option>'
        '<option value="read" selected>read</option>'
        '<option value="reread">reread</option>'
        '<option value="zope.Public">zope.Public</option>'
        '</select>'
        )

        widget.setRenderedValue(read_permission.id)
        self.assertEqual(widget(), out)

        self.assertRaises(WidgetInputError, widget.getInputValue)

        widget = SinglePermissionWidget(permissionField, request)

        request.form["field.TestName"] = 'read'
        
        self.assertEqual(widget.getInputValue(), read_permission.id)

        self.assertEqual(widget(), out)

        request.form["field.TestName.search"] = 'read'

        out = (
        '<input type="text" name="field.TestName.search" value="read">'
        '<select name="field.TestName">'
        '<option value="">---select permission---</option>'
        '<option value="read" selected>read</option>'
        '<option value="reread">reread</option>'
        '</select>'
        )
        self.assertEqual(widget(), out)


    def testPermissionWidget_w_public(self):
        read_permission = Permission('read', 'Read', 'Read something')
        ztapi.provideUtility(IPermission, read_permission, 'read')

        reread_permission = Permission('reread', 'ReRead', 'ReRead something')
        ztapi.provideUtility(IPermission, reread_permission, 'reread')

        request = TestRequest()

        permissionField = PermissionField(__name__ = 'TestName',
                                          title = u"This is a test",
                                          required=False)

        widget = SinglePermissionWidget(permissionField, request)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select permission---</option>'
        '<option value="read">read</option>'
        '<option value="reread">reread</option>'
        '<option value="zope.Public" selected>zope.Public</option>'
        '</select>'
        )

        widget.setRenderedValue(CheckerPublic)
        self.assertEqual(widget(), out)

        self.assertRaises(WidgetInputError, widget.getInputValue)

        widget = SinglePermissionWidget(permissionField, request)

        request.form["field.TestName"] = 'zope.Public'

        self.assertEqual(widget.getInputValue(), CheckerPublic)

        self.assertEqual(widget(), out)

        request.form["field.TestName"] = ''

        self.assertEqual(widget.getInputValue(), None)


def test_suite():
    return TestSuite((makeSuite(TestPermissionWidget),))

if __name__=='__main__':
    main(defaultTest='test_suite')
