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
"""XXX short summary goes here.

$Id$
"""
import unittest
from zope.app.tests import placelesssetup
from zope.app import zapi
from zope.app.security.interfaces import IAuthenticationService


def setUp(test):
    placelesssetup.setUp()
    services = zapi.getGlobalServices()
    services.defineService(zapi.servicenames.Authentication,
                           IAuthenticationService)

def test_suite():
    from zope.testing import doctest
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

