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
"""Registration Widget Tests

$Id: test_registrationstatuswidget.py,v 1.1 2004/03/13 18:01:18 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.publisher.browser import TestRequest
from zope.app.registration.interfaces import RegistrationStatus
from zope.app.registration.browser import RegistrationStatusWidget
from zope.app.tests.placelesssetup import PlacelessSetup


class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        
    def test_call(self):
        field = RegistrationStatus(__name__="status")
        request = TestRequest()
        widget = RegistrationStatusWidget(field, request)
        widget.setPrefix("f")

        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            u'<input class="radioType" checked="checked" id="f.status.0" '
            u'name="f.status" type="radio" value="Unregistered" />'
            u'<label for="f.status.0">Unregistered</label>&nbsp;&nbsp;'
            u'<input class="radioType" id="f.status.1" name="f.status" '
            u'type="radio" value="Registered" />'
            u'<label for="f.status.1">Registered</label>&nbsp;&nbsp;'
            u'<input class="radioType" id="f.status.2" name="f.status" '
            u'type="radio" value="Active" />'
            u'<label for="f.status.2">Active</label>')

        request.form['f.status'] = u'Registered'
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            u'<input class="radioType" id="f.status.0" name="f.status" '
            u'type="radio" value="Unregistered" /><label '
            u'for="f.status.0">Unregistered</label>'
            u'&nbsp;&nbsp;'
            u'<input class="radioType" checked="checked" id="f.status.1" '
            u'name="f.status" type="radio" value="Registered" /><label '
            u'for="f.status.1">Registered</label>'
            u'&nbsp;&nbsp;'
            u'<input class="radioType" id="f.status.2" name="f.status" '
            u'type="radio" value="Active" /><label '
            u'for="f.status.2">Active</label>')

        widget.setRenderedValue("Active")
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            u'<input class="radioType" id="f.status.0" name="f.status" '
            u'type="radio" value="Unregistered" />'
            u'<label for="f.status.0">Unregistered</label>'
            u'&nbsp;&nbsp;'
            u'<input class="radioType" id="f.status.1" name="f.status" '
            u'type="radio" value="Registered" />'
            u'<label for="f.status.1">Registered</label>'
            u'&nbsp;&nbsp;'
            u'<input class="radioType" checked="checked" id="f.status.2" '
            u'name="f.status" type="radio" value="Active" />'
            u'<label for="f.status.2">Active</label>'
            )

        widget.setRenderedValue(u"Unregistered")
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            u'<input class="radioType" checked="checked" id="f.status.0" '
            u'name="f.status" type="radio" value="Unregistered" />'
            u'<label for="f.status.0">Unregistered</label>&nbsp;&nbsp;'
            u'<input class="radioType" id="f.status.1" name="f.status" '
            u'type="radio" value="Registered" />'
            u'<label for="f.status.1">Registered</label>&nbsp;&nbsp;'
            u'<input class="radioType" id="f.status.2" name="f.status" '
            u'type="radio" value="Active" />'
            u'<label for="f.status.2">Active</label>')


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
