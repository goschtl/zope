##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
import doctest
import zope.testing.module
import zope.component
import zope.interface

import zope.app.testing.placelesssetup
import zope.app.security.interfaces
import zope.annotation.interfaces

import zc.notification.interfaces


class Principal(object):

    zope.interface.implements(
        zope.app.security.interfaces.IPrincipal)

    def __init__(self, id):
        self.id = id

class Authentication(object):

    zope.interface.implements(
        zope.app.security.interfaces.IAuthentication)

    def __init__(self):
        self._data = {}

    def getPrincipal(self, principal_id):
        try:
            principal = self._data[principal_id]
        except KeyError:
            principal = Principal(principal_id)
            self._data[principal_id] = principal
        return principal

class Annotations(dict):

    zope.interface.implements(
        zope.annotation.interfaces.IAnnotations)

    def __new__(class_, principal, context=None):
        try:
            annotations = principal.annotations
        except AttributeError:
            annotations = dict.__new__(class_)
            principal.annotations = annotations
        return annotations

    def __init__(self, principal, context=None):
        pass




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
    util = Authentication()
    zope.component.provideUtility(util)
    zope.component.provideAdapter(
        Annotations,
        (zope.app.security.interfaces.IPrincipal,),
        zope.annotation.interfaces.IAnnotations)
    zope.component.provideAdapter(
        Annotations,
        (zope.app.security.interfaces.IPrincipal, None),
        zope.annotation.interfaces.IAnnotations)
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
