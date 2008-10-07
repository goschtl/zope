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
""" z3ext Control Panel tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest, doctest
from zope import interface, component 
from zope.app.testing import setup
from zope.copypastemove import ObjectCopier
from zope.component.event import objectEventNotify
from zope.location.interfaces import ILocation
from zope.app.component.site import changeSiteConfigurationAfterMove
from zope.app.component.interfaces import ISite
from zope.app.container.interfaces import IObjectMovedEvent
from zope.app.container.contained import dispatchToSublocations

from z3ext.controlpanel.configlet import Configlet
from z3ext.controlpanel.testing import setUpControlPanel


def setUp(test):
    setup.placefulSetUp(True)

    component.provideAdapter(ObjectCopier)
    component.provideHandler(objectEventNotify)
    component.provideHandler(
        changeSiteConfigurationAfterMove, (ISite, IObjectMovedEvent))
    component.provideHandler(
        dispatchToSublocations, (ILocation, IObjectMovedEvent))

    setUpControlPanel()
    setup.setUpTestAsModule(test, 'z3ext.controlpanel.README')


def tearDown(test):
    setup.placefulTearDown()
    setup.tearDownTestAsModule(test)


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocFileSuite(
                'site.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'z3ext.controlpanel.storage',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'z3ext.controlpanel.configlettype',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
