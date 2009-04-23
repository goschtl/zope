##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
""" 

$Id$
"""
import unittest, doctest
from zope import interface
from zope.app.testing import functional
from zope.publisher.browser import BrowserRequest
from z3ext.controlpanel.testing import z3extControlPanelLayer

from interfaces import MySkin


def test_suite():
    interface.classImplements(BrowserRequest, MySkin)

    controlpanel = functional.FunctionalDocFileSuite(
        "README.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    controlpanel.layer = z3extControlPanelLayer

    return unittest.TestSuite((controlpanel,))
