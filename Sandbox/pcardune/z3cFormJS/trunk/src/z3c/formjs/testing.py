##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Common z3c.formks test setups

$Id: $
"""
__docformat__ = 'restructuredtext'

import os.path

import zope.interface
from zope.publisher.browser import TestRequest
from zope.app.testing import setup

import jquery.layer
from z3c.formjs import jsbutton

import browser

class TestRequest(TestRequest):
    zope.interface.implements(jquery.layer.IJQueryJavaScriptBrowserLayer)

def getPath(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)

def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}

def tearDown(test):
    setup.placefulTearDown()
