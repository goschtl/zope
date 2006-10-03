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
"""Test harness for zc.notification.
"""
__docformat__ = "reStructuredText"

import unittest

from zope.testing import doctest
import zope.testing.module
import zope.component
import zope.interface

import zope.app.principalannotation.interfaces
import zope.app.testing.placelesssetup

import zc.notification.interfaces

class PrincipalAnnotationUtility(object):

    zope.interface.implements(
        zope.app.principalannotation.interfaces.IPrincipalAnnotationUtility)

    def __init__(self):
        self._data = {}

    def getAnnotationsById(self, id):
        return self._data.setdefault(id, {})


class PrintNotifier(object):

    zope.interface.implements(
        zc.notification.interfaces.INotifier)

    def __init__(self, method=""):
        self.method = method

    def send(self, notification, principal_id, annotations, context):
        print notification.name
        print notification.message
        print principal_id, "by", repr(self.method)

def setUp(test):
    zope.app.testing.placelesssetup.setUp(test)
    util = PrincipalAnnotationUtility()
    zope.component.provideUtility(util)
    zope.component.provideUtility(PrintNotifier("email"), name="email")
    zope.component.provideUtility(PrintNotifier())

def requestlessSetUp(test):
    zope.app.testing.placelesssetup.setUp(test)
    zope.testing.module.setUp(test, 'zc.notification.requestless_txt')

def requestlessTearDown(test):
    zope.testing.module.tearDown(test)
    zope.app.testing.placelesssetup.tearDown(test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            "README.txt",
            setUp=setUp,
            tearDown=zope.app.testing.placelesssetup.tearDown),
        doctest.DocFileSuite(
            "requestless.txt",
            setUp=requestlessSetUp,
            tearDown=requestlessTearDown),
        ))
