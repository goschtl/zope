##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Browser code

$Id$
"""
__docformat__ = "reStructuredText"
from zope.app.publication import traversers
from zope.app.testing import placelesssetup, setup
from zope.publisher.interfaces.browser import IBrowserPublisher, IBrowserRequest
from zope.security import checker
from zope.site import folder
from zope.site.interfaces import IFolder
from zope.traversing.testing import setUp as traversalSetUp
import doctest
import unittest
import zope.component
import zope.interface

from z3c.mountpoint import interfaces, mountpoint

def setUp(test):
    placelesssetup.setUp(test)
    traversalSetUp()
    # The test traverser is all we need.
    zope.component.provideAdapter(
        traversers.TestTraverser,
        (zope.interface.Interface, IBrowserRequest), IBrowserPublisher)
    # A simple interface checker for: MountPoint
    checker.defineChecker(
        mountpoint.MountPoint, checker.InterfaceChecker(interfaces.IMountPoint))
    # A simple interface checker for: Folder
    checker.defineChecker(
        folder.Folder, checker.InterfaceChecker(IFolder))

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                     setUp=setUp, tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))
