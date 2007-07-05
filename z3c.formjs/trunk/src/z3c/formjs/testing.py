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
import jquery.layer
import os.path
import z3c.form.interfaces
import z3c.form.testing
import zope.interface
import zope.component
from z3c.form.interfaces import IWidget, IFormLayer
from zope.publisher.browser import TestRequest
from zope.app.testing import setup

from z3c.formjs import jsbutton, jswidget, jsevent
from z3c.formjs import interfaces, browser

class TestRequest(TestRequest):
    zope.interface.implements(jquery.layer.IJQueryJavaScriptBrowserLayer,
                              IFormLayer)

def getPath(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)


def setUpEventUtilities():
    ## Event Utilities
    zope.component.provideUtility(jsevent.CLICK, name='click')
    zope.component.provideUtility(jsevent.DBLCLICK, name='dblclick')
    zope.component.provideUtility(jsevent.LOAD, name='load')
    zope.component.provideUtility(jsevent.CHANGE, name='change')
    zope.component.provideUtility(jsevent.BLUR, name='blur')
    zope.component.provideUtility(jsevent.FOCUS, name='focus')
    zope.component.provideUtility(jsevent.KEYDOWN, name='keydown')
    zope.component.provideUtility(jsevent.KEYUP, name='keyup')
    zope.component.provideUtility(jsevent.MOUSEDOWN, name='mousedown')
    zope.component.provideUtility(jsevent.MOUSEMOVE, name='mousemove')
    zope.component.provideUtility(jsevent.MOUSEOUT, name='mouseout')
    zope.component.provideUtility(jsevent.MOUSEOVER, name='mouseover')
    zope.component.provideUtility(jsevent.MOUSEUP, name='mouseup')
    zope.component.provideUtility(jsevent.RESIZE, name='resize')
    zope.component.provideUtility(jsevent.SELECT, name='select')
    zope.component.provideUtility(jsevent.SUBMIT, name='submit')


def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}
    z3c.form.testing.setupFormDefaults()
    zope.component.provideAdapter(
        jsbutton.JSButtonAction, provides=z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        jswidget.JSEventsWidget, provides=interfaces.IJSEventsWidget)
    zope.component.provideAdapter(jsevent.JQueryEventRenderer)

    setUpEventUtilities()


def tearDown(test):
    setup.placefulTearDown()
