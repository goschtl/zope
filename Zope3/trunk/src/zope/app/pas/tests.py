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
from zope.interface import implements
from zope.app.zapi import getUtility

from zope.app.session.interfaces import \
        IClientId, IClientIdManager, ISession, ISessionDataContainer, \
        ISessionPkgData, ISessionData
from zope.app.session.session import \
        ClientId, Session, \
        PersistentSessionDataContainer, RAMSessionDataContainer
from zope.app.session.http import CookieClientIdManager

from zope.publisher.interfaces import IRequest
from zope.publisher.tests.httprequest import TestRequest

class TestClientId(object):
    implements(IClientId)
    def __new__(cls, request):
        return 'dummyclientidfortesting'

def sessionSetUp(session_data_container_class=PersistentSessionDataContainer):
    placelesssetup.setUp()
    ztapi.provideAdapter(IRequest, IClientId, TestClientId)
    ztapi.provideAdapter(IRequest, ISession, Session)
    ztapi.provideUtility(IClientIdManager, CookieClientIdManager())
    sdc = session_data_container_class()
    ztapi.provideUtility(ISessionDataContainer, sdc, '')

def formAuthSetUp(self):
    placefulSetUp(site=True)

def formAuthTearDown(self):
    placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.pas.generic'),
        doctest.DocTestSuite('zope.app.pas.httpplugins'),
        doctest.DocFileSuite('principalfolder.txt'),
        doctest.DocFileSuite('idpicker.txt'),
        doctest.DocTestSuite('zope.app.pas.principalplugins'),
        doctest.DocTestSuite('zope.app.pas.browserplugins',
                             setUp=formAuthSetUp,
                             tearDown=formAuthTearDown),
        doctest.DocFileSuite('README.txt',
                             setUp=placelesssetup.setUp,
                             tearDown=placelesssetup.tearDown,
                             globs={'provideUtility': ztapi.provideUtility,
                                    'getEvents': getEvents,
                                    }),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

