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
from zope.publisher.interfaces import IRequest
from zope.publisher.tests.httprequest import TestRequest

from zope.app import zapi
from zope.app.testing import placelesssetup, ztapi
from zope.app.event.tests.placelesssetup import getEvents
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

def groupSetUp(test):
    placelesssetup.setUp()

def searcheableSetUp(self):
    placefulSetUp(site=True)

def searcheableTearDown(self):
    placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.app.authentication.generic'),
        doctest.DocTestSuite('zope.app.authentication.httpplugins'),
        doctest.DocFileSuite('principalfolder.txt'),
        doctest.DocFileSuite('idpicker.txt'),
        doctest.DocTestSuite('zope.app.authentication.principalplugins'),
        doctest.DocTestSuite('zope.app.authentication.browserplugins',
                             setUp=formAuthSetUp,
                             tearDown=formAuthTearDown),
        doctest.DocFileSuite('README.txt',
                             setUp=searcheableSetUp,
                             tearDown=searcheableTearDown,
                             globs={'provideUtility': ztapi.provideUtility,
                                    'getEvents': getEvents,
                                    }),
        doctest.DocFileSuite('groupfolder.txt',
                             setUp=groupSetUp,
                             tearDown=placelesssetup.tearDown,
                             ),
        
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

