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
import z3c.form.testing

import jquery.layer
from z3c.formjs import jsbutton, jswidget, jsevent
from z3c.formjs import interfaces

from z3c.form.interfaces import IWidget
import browser

class TestRequest(TestRequest):
    zope.interface.implements(jquery.layer.IJQueryJavaScriptBrowserLayer)

def getPath(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)


def setUpEventUtilities():
    ## Event Utilities
    zope.component.provideUtility(jsevent.CLICK, interfaces.IJSEvent, name='click')
    zope.component.provideUtility(jsevent.DBLCLICK, interfaces.IJSEvent, name='dblclick')
    zope.component.provideUtility(jsevent.LOAD, interfaces.IJSEvent, name='load')
    zope.component.provideUtility(jsevent.CHANGE, interfaces.IJSEvent, name='change')
    zope.component.provideUtility(jsevent.BLUR, interfaces.IJSEvent, name='blur')
    zope.component.provideUtility(jsevent.FOCUS, interfaces.IJSEvent, name='focus')
    zope.component.provideUtility(jsevent.KEYDOWN, interfaces.IJSEvent, name='keydown')
    zope.component.provideUtility(jsevent.KEYUP, interfaces.IJSEvent, name='keyup')
    zope.component.provideUtility(jsevent.MOUSEDOWN, interfaces.IJSEvent, name='mousedown')
    zope.component.provideUtility(jsevent.MOUSEMOVE, interfaces.IJSEvent, name='mousemove')
    zope.component.provideUtility(jsevent.MOUSEOUT, interfaces.IJSEvent, name='mouseout')
    zope.component.provideUtility(jsevent.MOUSEOVER, interfaces.IJSEvent, name='mouseover')
    zope.component.provideUtility(jsevent.MOUSEUP, interfaces.IJSEvent, name='mouseup')
    zope.component.provideUtility(jsevent.RESIZE, interfaces.IJSEvent, name='resize')
    zope.component.provideUtility(jsevent.SELECT, interfaces.IJSEvent, name='select')
    zope.component.provideUtility(jsevent.SUBMIT, interfaces.IJSEvent, name='submit')


def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}
    z3c.form.testing.setupFormDefaults()
    zope.component.provideAdapter(jsbutton.JSButtonAction,
                                  (jquery.layer.IJQueryJavaScriptBrowserLayer,
                                   interfaces.IJSButton),
                                  z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(jswidget.JSEventsWidget,
                                  (interfaces.IJSEvents, IWidget),
                                  interfaces.IJSEventsWidget)
    setUpEventUtilities()


def tearDown(test):
    setup.placefulTearDown()
