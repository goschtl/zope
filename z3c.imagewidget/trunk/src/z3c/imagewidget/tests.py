##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Image Widgets Test

$Id$
"""
__docformat__ = "reStructuredText"
import doctest
import unittest
import zope.component
from zope.app.session import interfaces
from zope.app.session import session
from zope.app.testing import setup
from zope.app.session.http import CookieClientIdManager
from zope.publisher.interfaces import IRequest
from zope.testing.doctestunit import DocFileSuite
from z3c.image.proc.adapter import ProcessableImage

def setUp(test):
    setup.placefulSetUp()
    zope.component.provideAdapter(
        session.ClientId, (IRequest,), interfaces.IClientId)
    zope.component.provideAdapter(
        session.Session, (IRequest,), interfaces.ISession)
    zope.component.provideUtility(
        CookieClientIdManager(), interfaces.IClientIdManager)
    zope.component.provideUtility(
        session.PersistentSessionDataContainer(),
        interfaces.ISessionDataContainer)
    zope.component.provideAdapter(ProcessableImage)


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
