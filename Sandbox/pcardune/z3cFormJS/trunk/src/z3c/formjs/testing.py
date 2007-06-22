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
import zope.component
from zope.publisher.browser import TestRequest
from zope.app.testing import setup
import z3c.form.interfaces

import jquery.layer
from z3c.formjs import jsbutton, jswidget
from z3c.formjs import interfaces

from z3c.form.interfaces import IWidget
import browser

class TestRequest(TestRequest):
    zope.interface.implements(jquery.layer.IJQueryJavaScriptBrowserLayer)

def getPath(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)

def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}
    zope.component.provideAdapter(jsbutton.JSButtonAction,
                                  (jquery.layer.IJQueryJavaScriptBrowserLayer,
                                   interfaces.IJSButton),
                                  z3c.form.interfaces.IFieldWidget)

    zope.component.provideAdapter(jswidget.JSEventsWidget,
                                  (interfaces.IJSEvents, IWidget),
                                  interfaces.IJSEventsWidget)

def tearDown(test):
    setup.placefulTearDown()
