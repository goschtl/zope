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
"""ComponentLocationWidget tests.

$Id: test_field_widget.py,v 1.2 2002/12/19 20:38:24 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.Traversing import traverse
from Interface import Interface
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.App.OFS.Services.Browser.field import ComponentLocationWidget

class FakeComponentLocation:

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
        default = traverse(self.rootFolder,
                           '++etc++Services/Packages/default')
        default.setObject('c1', C())
        default.setObject('c2', C())
        default.setObject('c3', C())
        default.setObject('d1', D())
        default.setObject('d2', D())
        default.setObject('d3', D())

        request = TestRequest()

        fake = FakeComponentLocation(default, I1)
        widget = ComponentLocationWidget(fake, request)

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
        fake = FakeComponentLocation(None, I1)
        widget = ComponentLocationWidget(fake, request)
        self.assertEqual(widget._convert(u''), None)
        self.assertEqual(widget._convert(u'/a'), u'/a')
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
