##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test forms

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeDocTestSuite
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Testing.ZopeTestCase import installProduct
installProduct('Five')

def test_get_widgets_for_schema_fields():
    """
    >>> from zope.schema import Choice, TextLine
    >>> salutation = Choice(title=u'Salutation',
    ...                     values=("Mr.", "Mrs.", "Captain", "Don"))
    >>> contactname = TextLine(title=u'Name')

    >>> from Products.Five.traversable import FakeRequest
    >>> request = FakeRequest()
    >>> salutation = salutation.bind(request)
    >>> contactname = contactname.bind(request)

    >>> from zope.app import zapi
    >>> from zope.app.form.interfaces import IInputWidget
    >>> from zope.app.form.browser.textwidgets import TextWidget
    >>> from zope.app.form.browser.itemswidgets import DropdownWidget

    >>> view1 = zapi.getViewProviding(contactname, IInputWidget, request)
    >>> view1.__class__ == TextWidget
    True

    >>> view2 = zapi.getViewProviding(salutation, IInputWidget, request)
    >>> view2.__class__ == DropdownWidget
    True
    """

def setUpForms(self):
    uf = self.folder.acl_users
    uf._doAddUser('viewer', 'secret', [], [])
    uf._doAddUser('manager', 'r00t', ['Manager'], [])
    import Products.Five.form.tests
    from Products.Five import zcml
    zcml.load_config('configure.zcml', package=Products.Five.form.tests)

def test_suite():
    return unittest.TestSuite((
            ZopeDocTestSuite(),
            FunctionalDocFileSuite(
		'forms.txt',
		package="Products.Five.form.tests",
		setUp=setUpForms),
            ))

if __name__ == '__main__':
    framework()
