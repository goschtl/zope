##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pluggable Authentication Service Tests

$Id$
"""
__docformat__ = "reStructuredText"
import unittest
from zope.testing import doctest
from zope.app.tests import placelesssetup, ztapi
from zope.app.event.tests.placelesssetup import getEvents
from zope.app.tests.setup import placefulSetUp, placefulTearDown

from zope.app.session.interfaces import \
        IClientId, IClientIdManager, ISession, ISessionDataContainer, \
        ISessionPkgData, ISessionData
from zope.app.session.session import \
        ClientId, Session, \
        PersistentSessionDataContainer, RAMSessionDataContainer
from zope.app.session.http import CookieClientIdManager

from zope.publisher.interfaces import IRequest
from zope.publisher.tests.httprequest import TestRequest

def sessionSetUp(session_data_container_class=PersistentSessionDataContainer):
    placelesssetup.setUp()
    ztapi.provideAdapter(IRequest, IClientId, ClientId)
    ztapi.provideAdapter(IRequest, ISession, Session)
    ztapi.provideUtility(IClientIdManager, CookieClientIdManager())
    sdc = session_data_container_class()
    ztapi.provideUtility(ISessionDataContainer, sdc, 'pas_credentials')

def formAuthSetUp(self):
    placefulSetUp(site=True)

def formAuthTearDown(self):
    placefulTearDown()

def createTestRequest(**kw):
    return TestRequest(**kw)

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.pas.httpplugin'),
        doctest.DocFileSuite('README.txt',
                             setUp=placelesssetup.setUp,
                             tearDown=placelesssetup.tearDown,
                             globs={'provideUtility': ztapi.provideUtility,
                                    'getEvents': getEvents,
                                    }),
        doctest.DocTestSuite('zope.app.pas.browserplugins',
                             setUp=formAuthSetUp,
                             tearDown=formAuthTearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

