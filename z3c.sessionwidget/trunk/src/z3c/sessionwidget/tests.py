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
import doctest
import zope.component
from zope.app.session import interfaces
from zope.app.session import session
from zope.app.testing import placelesssetup
from zope.app.session.http import CookieClientIdManager
from zope.publisher.interfaces import IRequest


def setUp(test):
    placelesssetup.setUp()
    zope.component.provideAdapter(
        session.ClientId, (IRequest,), interfaces.IClientId)
    zope.component.provideAdapter(
        session.Session, (IRequest,), interfaces.ISession)
    zope.component.provideUtility(
        CookieClientIdManager(), interfaces.IClientIdManager)
    zope.component.provideUtility(
        session.PersistentSessionDataContainer(),
        interfaces.ISessionDataContainer)


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp, tearDown=placelesssetup.tearDown(),
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
