##############################################################################
#
# Copyright (c) 2006 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test harness for zc.notification.email.

"""
__docformat__ = "reStructuredText"

import unittest
from zope.testing import doctest

import zope.component
import zope.interface

import zope.app.security.interfaces
import zope.app.testing.placelesssetup

import zc.notification.interfaces
import zc.notification.tests


class Authentication(object):

    zope.interface.implements(
        zope.app.security.interfaces.IAuthentication)

    def getPrincipal(self, id):
        return Principal(id)


class Principal(object):

    zope.interface.implements(
        zope.app.security.interfaces.IPrincipal)

    def __init__(self, id):
        self.id = id


def setUp(test):
    zope.app.testing.placelesssetup.setUp(test)
    zope.component.provideUtility(Authentication())
    zope.component.provideUtility(
        zc.notification.tests.PrincipalAnnotationUtility())

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            "README.txt",
            setUp=setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
        doctest.DocFileSuite(
            "view.txt",
            setUp=zope.app.testing.placelesssetup.setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown),
        ))
