##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" z3ext.statusmessage tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest, doctest
from zope.app.testing import setup

from zope import interface, component
from zope.component import provideAdapter
from zope.session.interfaces import ISession
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import provideUtility

import browser


class Session(dict):

    def __getitem__(self, key):
        if not self.has_key(key):
            self[key] = {}

        return super(Session, self).__getitem__(key)

session = Session()

@interface.implementer(ISession)
@component.adapter(IBrowserRequest)
def getSession(request):
    return session


def setUp(test):
    setup.placelessSetUp()
    provideAdapter(getSession)
    provideAdapter(browser.StatusMessage, name='statusMessage')
    provideAdapter(browser.Message)
    provideAdapter(browser.InformationMessage)
    provideAdapter(browser.ErrorMessage)
    provideAdapter(browser.WarningMessage)


def tearDown(test):
    session.__init__()
    setup.placelessTearDown()
    

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
