# -*- coding: ascii -*-
##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
'''
$Id: test_session.py,v 1.2 2004/02/09 05:16:33 Zen Exp $
'''

import unittest, doctest
from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.tests import setup
import zope.interface
from zope.app.interfaces.services.utility import ILocalUtility
from zope.app.services.utility import LocalUtilityService
from zope.app.services.servicenames import Utilities
from zope.app.interfaces.annotation import IAttributeAnnotatable

from zope.app.interfaces.utilities.session import \
        IBrowserId, IBrowserIdManager, ISession, ISessionDataContainer

from zope.app.utilities.session import \
        CookieBrowserIdManager, Session, getSession, \
        PersistentSessionDataContainer

from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.http import HTTPRequest

def test_CookieBrowserIdManager():
    """
    CookieBrowserIdManager.generateUniqueId should generate a unique
    IBrowserId each time it is called

    >>> csu = CookieBrowserIdManager()
    >>> id1 = csu.generateUniqueId()
    >>> id2 = csu.generateUniqueId()
    >>> id1 != id2
    True
    >>> IBrowserId.isImplementedBy(id1)
    True
    >>> IBrowserId.isImplementedBy(id2)
    True

    CookieBrowserIdManager.getRequestId pulls the IBrowserId from an
    IHTTPRequest, or returns None if there isn't one stored in it.
    Because cookies cannnot be trusted, we confirm that they are not forged,
    returning None if we have a corrupt or forged browser id.
    
    >>> request = HTTPRequest(None, None, {}, None)
    >>> csu.getRequestId(request) is None
    True
    >>> csu.setRequestId(request, id1)
    >>> csu.getRequestId(request) == id1
    True
    >>> csu.setRequestId(request, 'invalid_id')
    >>> csu.getRequestId(request) is None
    True

    Make sure that the same browser id is extracted from a cookie in
    request (sent from the browser) and a cookie in request.response
    (set during this transaction)

    >>> request2 = HTTPRequest(None, None, {}, None)
    >>> request2._cookies = request.response._cookies
    >>> csu.getRequestId(request) == csu.getRequestId(request2)
    True

    CookieBrowserIdManager.getBrowserId pulls the IBrowserId from an
    IHTTPRequest, or generates a new one and returns it after storing
    it in the request.

    >>> id3 = csu.getBrowserId(request)
    >>> id4 = csu.getBrowserId(request)
    >>> str(id3) == str(id4)
    True
    >>> id3 == id4
    True

    Confirm the path of the cookie is correct. The value being tested
    for here will eventually change - it should be the URL to the
    site containing the CookieBrowserIdManager

    >>> cookie = request.response.getCookie(csu.namespace)
    >>> cookie['path'] == request.getApplicationURL(path_only=True)
    True

    XXX: Confirm the expiry time of the cookie is correct.
    XXX: >>> expires = strptime(cookie['expires'])

    """

def test_PersistentSessionIdContainer():
    """
    >>> sdc = PersistentSessionDataContainer()
    >>> sdc['a']
    Traceback (most recent call last):
    File "<stdin>", line 1, in ?
    File "/usr/python-2.3.3/lib/python2.3/UserDict.py", line 19, in __getitem__
        def __getitem__(self, key): return self.data[key]
    KeyError: 'a'
    >>> from zodb.btrees.OOBTree import OOBTree
    >>> sdc['a'] = OOBTree()
    >>> pdict = OOBTree()
    >>> sdc['a'] = pdict
    >>> id(pdict) == id(sdc['a'])
    True
    >>> del sdc['a']
    >>> sdc['a']
    Traceback (most recent call last):
    File "<stdin>", line 1, in ?
    File "/usr/python-2.3.3/lib/python2.3/UserDict.py", line 19, in __getitem__
        def __getitem__(self, key): return self.data[key]
    KeyError: 'a'
    >>> del sdc['a']
    Traceback (most recent call last):
    File "<stdin>", line 1, in ?
    File "/usr/python-2.3.3/lib/python2.3/UserDict.py", line 21, in __delitem__
        def __delitem__(self, key): del self.data[key]
    KeyError: 'a'
    """

def test_Session():
    """
    >>> data_container = PersistentSessionDataContainer()
    >>> session = Session(data_container, 'browser id', 'zopeproducts.foo')
    >>> session['color']
    Traceback (most recent call last):
    File "<stdin>", line 1, in ?
    File "zope/app/utilities/session.py", line 157, in __getitem__
        return self._data[key]
    KeyError: 'color'
    >>> session['color'] = 'red'
    >>> session['color']
    'red'

    And make sure no namespace conflicts...

    >>> session2 = Session(data_container, 'browser id', 'zopeproducts.bar')
    >>> session2['color'] = 'blue'
    >>> session['color']
    'red'
    >>> session2['color']
    'blue'

    Test the rest of the dictionary interface...

    >>> 'foo' in session
    False
    >>> 'color' in session
    True
    >>> session.get('size', 'missing')
    'missing'
    >>> session.get('color', 'missing')
    'red'
    >>> list(session.keys())
    ['color']
    >>> list(session.values())
    ['red']
    >>> list(session.items())
    [('color', 'red')]
    >>> len(session)
    1
    >>> [x for x in session]
    ['color']
    >>> del session['color']
    >>> session.get('color', 'missing')
    'missing'
    """


def test_localutilities():
    """
    Setup a placeful environment with a IBrowserIdManager
    and ISessionDataContainer

    >>> root = setup.placefulSetUp(site=True)
    >>> setup.createStandardServices(root)
    >>> sm = setup.createServiceManager(root)
    >>> us = setup.addService(sm, Utilities, LocalUtilityService())
    >>> idmanager = CookieBrowserIdManager()
    >>> zope.interface.directlyProvides(idmanager,
    ...                                 IAttributeAnnotatable, ILocalUtility)
    >>> bim = setup.addUtility(
    ...     sm, '', IBrowserIdManager, idmanager, 'test')
    >>> pdc = PersistentSessionDataContainer()
    >>> zope.interface.directlyProvides(pdc,
    ...                                 IAttributeAnnotatable, ILocalUtility)
    >>> sdc = setup.addUtility(sm, 'persistent', ISessionDataContainer, pdc)
    >>> sdc = setup.addUtility(sm, 'products.foo',ISessionDataContainer, pdc)
    >>> sdc = setup.addUtility(sm, 'products.bar', ISessionDataContainer, pdc)
    >>> request = HTTPRequest(None, None, {}, None)
   
    Make sure we can access utilities

    >>> sdc = zapi.getUtility(root, ISessionDataContainer, 'persistent')
    >>> bim = zapi.getUtility(root, IBrowserIdManager)

    Make sure getSession works

    >>> session1 = getSession(root, request, 'products.foo')
    >>> session2 = getSession(root, request, 'products.bar', 'persistent')
    >>> session3 = getSession(root, request, 'products.baz', pdc)

    Make sure it returned sane values

    >>> ISession.isImplementedBy(session1)
    True
    >>> ISession.isImplementedBy(session2)
    True
    >>> ISession.isImplementedBy(session3)
    True

    Make sure that product_ids don't share a namespace

    >>> session1['color'] = 'red'
    >>> session2['color'] = 'blue'
    >>> session1['color']
    'red'
    >>> session2['color']
    'blue'

    >>> setup.placefulTearDown()
    >>> 'Thats all folks!'
    'Thats all folks!'
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))

if __name__ == '__main__':
    unittest.main()

# vim: set filetype=python ts=4 sw=4 et si


