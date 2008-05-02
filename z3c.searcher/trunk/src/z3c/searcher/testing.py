###############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id:$
"""

import zope.component
from zope.publisher.interfaces import IRequest
from zope.session import session
from zope.session.http import CookieClientIdManager
from zope.session.interfaces import IClientId
from zope.session.interfaces import IClientIdManager
from zope.session.interfaces import ISession
from zope.session.interfaces import ISessionDataContainer
from zope.app.authentication.tests import TestClientId
from zope.app.keyreference.testing import SimpleKeyReference
from zope.app.testing import setup


def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}

    # session setup
    zope.component.provideAdapter(TestClientId, (IRequest,), IClientId)
    zope.component.provideAdapter(session.Session, (IRequest,), ISession)
    zope.component.provideUtility(CookieClientIdManager(), IClientIdManager)
    rsdc = session.RAMSessionDataContainer()
    zope.component.provideUtility(rsdc, ISessionDataContainer, '')

    # Setup simple key reference adapter
    zope.component.provideAdapter(SimpleKeyReference)

    from zope.app.pagetemplate import metaconfigure
    from z3c.macro import tales
    metaconfigure.registerType('macro', tales.MacroExpression)

    # register provider TALES
    from zope.app.pagetemplate import metaconfigure
    from zope.contentprovider import tales
    metaconfigure.registerType('provider', tales.TALESProviderExpression)


def tearDown(test):
    setup.placefulTearDown()
