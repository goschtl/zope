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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_registrationstatuswidget.py,v 1.1 2003/06/21 21:22:03 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.publisher.browser import TestRequest
from zope.app.interfaces.services.registration import RegistrationStatus
from zope.app.browser.services.registration import RegistrationStatusWidget

class Test(TestCase):

    def test_call(self):
        field = RegistrationStatus(__name__="status")
        request = TestRequest()
        widget = RegistrationStatusWidget(field, request)
        widget.setPrefix("f")

        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            '<label><input type="radio" name="f.status" value="Unregistered"'
            ' checked>'
            '&nbsp;Unregistered</label> '
            '<label><input type="radio" name="f.status" value="Registered">'
            '&nbsp;Registered</label> '
            '<label><input type="radio" name="f.status" value="Active">'
            '&nbsp;Active</label>'
            )

        request.form['f.status'] = u'Registered'
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            '<label><input type="radio" name="f.status" value="Unregistered">'
            '&nbsp;Unregistered</label> '
            '<label><input type="radio" name="f.status" value="Registered"'
            ' checked>'
            '&nbsp;Registered</label> '
            '<label><input type="radio" name="f.status" value="Active">'
            '&nbsp;Active</label>'
            )

        widget.setData("Active")
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            '<label><input type="radio" name="f.status" value="Unregistered">'
            '&nbsp;Unregistered</label> '
            '<label><input type="radio" name="f.status" value="Registered">'
            '&nbsp;Registered</label> '
            '<label><input type="radio" name="f.status" value="Active"'
            ' checked>'
            '&nbsp;Active</label>'
            )

        widget.setData(u"Unregistered")
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            '<label><input type="radio" name="f.status" value="Unregistered"'
            ' checked>'
            '&nbsp;Unregistered</label> '
            '<label><input type="radio" name="f.status" value="Registered">'
            '&nbsp;Registered</label> '
            '<label><input type="radio" name="f.status" value="Active">'
            '&nbsp;Active</label>'
            )


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
