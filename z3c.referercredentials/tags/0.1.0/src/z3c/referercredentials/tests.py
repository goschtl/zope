##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTTP-Referer Credentials Test Setup

$Id$
"""
__docformat__ = "reStructuredText"
import unittest
import zope.component
from zope.app.session import session, http, interfaces
from zope.app.testing import placelesssetup
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite

def setUp(test):
    placelesssetup.setUp()
    zope.component.provideAdapter(session.ClientId)
    zope.component.provideAdapter(session.Session)
    zope.component.provideUtility(
        http.CookieClientIdManager(), interfaces.IClientIdManager)
    zope.component.provideUtility(
        session.PersistentSessionDataContainer(),
        interfaces.ISessionDataContainer)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
