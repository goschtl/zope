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
"""ComponentPathWidget tests.

$Id: test_field_widget.py,v 1.3 2003/01/09 17:28:42 stevea Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.interface import Interface
from zope.app.services.service import ServiceManager
from zope.publisher.browser import TestRequest
from zope.app.browser.services.field import ComponentPathWidget

class FakeComponentPath:

    default = None

    def __init__(self, context, type):
        self.context = context
        self.type = type

    def validate(self, value): pass

    __name__ = 'X'

class I1(Interface):  pass

class I2(Interface):  pass

class C:
    __implements__ = I1

class D:
    __implements__ = I2

class Test(PlacefulSetup, TestCase):

    def test(self):
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        default = traverse(self.rootFolder, '++etc++Services/Packages/default')
        default.setObject('c1', C())
        default.setObject('c2', C())
        default.setObject('c3', C())
        default.setObject('d1', D())
        default.setObject('d2', D())
        default.setObject('d3', D())

        request = TestRequest()

        fake = FakeComponentPath(default, I1)
        widget = ComponentPathWidget(fake, request)

        expected = (
            '<select name="field.X">\n'
            '<option></option>\n'
            '<option>/++etc++Services/Packages/default/c1</option>\n'
            '<option>/++etc++Services/Packages/default/c2</option>\n'
            '<option>/++etc++Services/Packages/default/c3</option>\n'
            '</select>'
            )

        self.assertEqual(widget(), expected)

        request.form['field.X'] = u'/++etc++Services/Packages/default/c2'

        expected = (
            '<select name="field.X">\n'
            '<option></option>\n'
            '<option>/++etc++Services/Packages/default/c1</option>\n'
            '<option selected>/++etc++Services/Packages/default/c2</option>\n'
            '<option>/++etc++Services/Packages/default/c3</option>\n'
            '</select>'
            )

        self.assertEqual(widget(), expected)

    def test_convert(self):
        request = TestRequest()
        fake = FakeComponentPath(None, I1)
        widget = ComponentPathWidget(fake, request)
        self.assertEqual(widget._convert(u''), None)
        self.assertEqual(widget._convert(u'/a'), u'/a')


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
