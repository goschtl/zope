##############################################################################
#
# Copyright (c) 2003 Zope Corporation. All Rights Reserved.
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
import unittest
from zope.app.testing import placelesssetup
from zope import component, interface
import zope.publisher.interfaces.browser
import zope.schema.interfaces
import zope.app.form.browser
from zc.sharing import policy
import zc.sharing.sharing
import zc.table.interfaces
import zc.table.table

class ICon:
    
    def __init__(self, name):
        self.name = name

    def __call__(self, request=None):
        if request is None:
            return 'http://mysite/%s' % self.name
            
        return self

def sharingSetUp(test):
    placelesssetup.setUp(test)
    component.provideAdapter(
        zope.app.form.browser.CheckBoxWidget,
        (zope.schema.interfaces.IBool,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ),
        zope.app.form.interfaces.IInputWidget)
    component.provideAdapter(
        ICon('user_icon.gif'),
        [zope.publisher.interfaces.browser.IBrowserRequest],
        interface.Interface, 'user_icon.gif')
    component.provideAdapter(
        ICon('group_icon.gif'),
        [zope.publisher.interfaces.browser.IBrowserRequest],
        interface.Interface, 'group_icon.gif')
    interface.directlyProvides(zc.table.table.FormFullFormatter,
                               zc.table.interfaces.IFormatterFactory)
    component.provideUtility(zc.table.table.FormFullFormatter,
                             zc.table.interfaces.IFormatterFactory)

def sharingTearDown(test):
    placelesssetup.tearDown()
    zc.sharing.sharing.clearPrivileges()

def test_suite():
    from zope.testing import doctest
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'sharing.txt',
            setUp=sharingSetUp, tearDown=sharingTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

