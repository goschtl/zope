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
from zope.interface import implements
from zope.component import provideUtility, provideAdapter
from zope.publisher.interfaces import IRequest
from zope.publisher.tests.httprequest import TestRequest

from zope.app import zapi
from zope.app.testing import placelesssetup, ztapi
from zope.app.event.tests.placelesssetup import getEvents, clearEvents
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.app.session.interfaces import \
        IClientId, IClientIdManager, ISession, ISessionDataContainer, \
        ISessionPkgData, ISessionData
from zope.app.session.session import \
        ClientId, Session, \
        PersistentSessionDataContainer, RAMSessionDataContainer
from zope.app.session.http import CookieClientIdManager


class TestClientId(object):
    implements(IClientId)
    def __new__(cls, request):
        return 'dummyclientidfortesting'

def siteSetUp(test):
    placefulSetUp(site=True)

def siteTearDown(test):
    placefulTearDown()

def sessionSetUp(session_data_container_class=PersistentSessionDataContainer):
    placelesssetup.setUp()
    ztapi.provideAdapter(IRequest, IClientId, TestClientId)
    ztapi.provideAdapter(IRequest, ISession, Session)
    ztapi.provideUtility(IClientIdManager, CookieClientIdManager())
    sdc = session_data_container_class()
    ztapi.provideUtility(ISessionDataContainer, sdc, '')

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.authentication.generic'),
        doctest.DocTestSuite('zope.app.authentication.httpplugins'),
        doctest.DocFileSuite('principalfolder.txt'),
        doctest.DocTestSuite('zope.app.authentication.principalfolder',
                             setUp=placelesssetup.setUp,
                             tearDown=placelesssetup.tearDown),
        doctest.DocTestSuite('zope.app.authentication.idpicker'),
        doctest.DocTestSuite('zope.app.authentication.session',
                             setUp=siteSetUp,
                             tearDown=siteTearDown),
        doctest.DocFileSuite('README.txt',
                             setUp=siteSetUp,
                             tearDown=siteTearDown,
                             globs={'provideUtility': provideUtility,
                                    'provideAdapter': provideAdapter,
                                    'getEvents': getEvents,
                                    'clearEvents': clearEvents,
                                    'subscribe': ztapi.subscribe,
                                    }),
        doctest.DocFileSuite('groupfolder.txt',
                             setUp=placelesssetup.setUp,
                             tearDown=placelesssetup.tearDown,
                             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
