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
"""Tests for the Class Documentation Module

$Id: tests.py,v 1.1 2004/03/28 23:40:12 srichter Exp $
"""
import unittest
from zope.interface import Interface, directlyProvides
from zope.publisher.browser import TestRequest
from zope.testing.doctestunit import DocTestSuite
from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import setUp, tearDown

from zope.app.traversing.browser import AbsoluteURL, SiteAbsoluteURL
from zope.app.traversing.interfaces import ITraversable, ITraverser
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.location import LocationPhysicallyLocatable
from zope.app.traversing.adapters import RootPhysicallyLocatable
from zope.app.traversing.adapters import Traverser

from zope.app.apidoc.classmodule import ClassModule
from zope.app.apidoc.classmodule.browser import ClassDetails, ModuleDetails
from zope.app.apidoc.interfaces import IDocumentationModule


def browserSetUp():
    setUp()
    module = ClassModule()
    module.__name__ = ''
    directlyProvides(module, IContainmentRoot)
    ztapi.provideUtility(IDocumentationModule, module, "Class")

    ztapi.provideAdapter(
        None, ITraverser, Traverser)
    ztapi.provideAdapter(
        None, ITraversable, DefaultTraversable)
    ztapi.provideAdapter(
        None, IPhysicallyLocatable, LocationPhysicallyLocatable)
    ztapi.provideAdapter(
        IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)

    ztapi.browserView(Interface, "absolute_url", AbsoluteURL)
    ztapi.browserView(IContainmentRoot, "absolute_url", SiteAbsoluteURL)


def browserTearDown():
    tearDown()


def getClassDetailsView():
    cm = zapi.getUtility(None, IDocumentationModule, 'Class')
    view = ClassDetails()
    view.context = zapi.traverse(cm, 'zope/app/apidoc/classmodule/ClassModule')
    view.request = TestRequest()
    return view


def getModuleDetailsView():
    cm = zapi.getUtility(None, IDocumentationModule, 'Class')
    view = ModuleDetails()
    view.context = zapi.traverse(cm, 'zope/app/apidoc/classmodule')
    view.request = TestRequest()
    return view


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.apidoc.classmodule.browser',
                     setUp=browserSetUp, tearDown=browserTearDown),
        DocTestSuite('zope.app.apidoc.classmodule'),
        ))

if __name__ == '__main__':
    unittest.main()
