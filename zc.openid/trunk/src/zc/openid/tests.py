##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

import time
import unittest
import sys

from zope.component import provideAdapter
from zope.component import provideUtility
from zope.publisher.interfaces import IRequest
from zope.session.http import CookieClientIdManager
from zope.session.interfaces import IClientIdManager
from zope.session.interfaces import ISessionDataContainer
from zope.session.session import ClientId
from zope.session.session import RAMSessionDataContainer
from zope.session.session import Session
from zope.testing import doctest
from zope.testing.cleanup import cleanUp
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.browser.absoluteurl import AbsoluteURL

from openid.association import Association
from openid.consumer.consumer import AuthRequest
from openid.consumer.consumer import SuccessResponse
from openid.consumer.discover import OpenIDServiceEndpoint


def configure():
    """Set up global configuration for the unit tests.

    This includes session support that does not require ZODB.
    """
    provideUtility(CookieClientIdManager(), IClientIdManager)
    provideUtility(RAMSessionDataContainer(), ISessionDataContainer)
    provideAdapter(Session)
    provideAdapter(ClientId)
    provideAdapter(
        AbsoluteURL, adapts=(None, IRequest), provides=IAbsoluteURL)


xrds_template = """\
<?xml version="1.0" encoding="UTF-8"?>
<xrds:XRDS
    xmlns:xrds="xri://$xrds"
    xmlns="xri://$xrd*($v*2.0)">
  <XRD>
    <Service priority="0">
      <Type>http://specs.openid.net/auth/2.0/signon</Type>
      <Type>http://openid.net/signon/1.0</Type>
      <URI>http://example.com/openidserver</URI>
      <LocalID>%s</LocalID>
    </Service>
  </XRD>
</xrds:XRDS>
"""


class MockConsumer(object):
    """Mock implementation of openid.consumer.consumer.Consumer for testing.
    """

    def __init__(self, session, store):
        self.session = session
        self.store = store
        self.association = Association(
            # some of this data was sampled from a live example session.
            handle=u'{HMAC-SHA1}{49a5be49}{co7U9w==}',
            secret='0' * 20,
            issued=1234567890,
            lifetime=sys.maxint,
            assoc_type=u'HMAC-SHA1'
            )

    def begin(self, url):
        endpoints = OpenIDServiceEndpoint.fromXRDS(url, xrds_template % url)
        endpoint = endpoints[0]
        return AuthRequest(endpoints[0], self.association)

    def complete(self, form_data, app_url):
        return SuccessResponse()


def setUp(doctest=None):
    cleanUp()

def tearDown(doctest=None):
    cleanUp()


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            'unittests.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
    ])

if __name__ == '__main__':
    unittest.main()
