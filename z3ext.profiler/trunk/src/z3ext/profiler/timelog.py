##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
import time, sys
from datetime import datetime

from zope.component import queryMultiAdapter
from z3ext.layoutform.interfaces import ISaveAction
from z3ext.layoutform import button, Fields, PageletEditForm
from z3ext.wizard.step import WizardStepForm
from z3ext.layout.tales import PageletExpression
from z3ext.layout.pagelet import PageletPublisher, queryPagelet
from z3ext.portlet.manager import PortletManagerBase
from z3ext.portlet.interfaces import IPortletManagerView
from z3ext.pageelement.tales import PageelementExpression
from z3ext.pageelement.interfaces import IPageElement
from z3ext.statusmessage.interfaces import IStatusMessage

from interfaces import profilerEnabled


class TimeLogger(WizardStepForm, PageletEditForm):

    @button.buttonAndHandler(u'Start logger')
    def handleStartLogger(self, action):
        if profilerEnabled:
            IStatusMessage(self.request).add(
                u'Can not start logger. Another logger or profiler is running.',
                'warning')
        else:
            configlet = self.getContent()

            installLogger()
            IStatusMessage(self.request).add(
                u'Time logger has been started.')

    @button.buttonAndHandler(u'Stop logger')
    def handleStopLogger(self, action):
        uninstallLogger()
        IStatusMessage(self.request).add(u'Time logger has been stoped.')


_names = []

originalRenderPagelet = PageletExpression.render
originalGetitemPagelet = PageletPublisher.__getitem__
originalPortletMethod = PortletManagerBase.render
originalPageelementMethod = PageelementExpression.__call__


def renderPortletManager(self):
    if not self.portlets or not self.isAvailable():
        return u''

    view = queryMultiAdapter((self, self.request), IPortletManagerView)
    if view is not None:
        return view.updateAndRender()

    portlets = []

    for portlet in self.portlets:
        dt = datetime.now()
        rendered = portlet.updateAndRender()
        td = datetime.now() - dt
        secs = (td.days*86400+td.seconds)+(0.000001*td.microseconds)
        print >>sys.stderr, 'portlet:      ', '%0.6f'%secs, portlet.__name__

        portlets.append(rendered)

    return u'\n'.join(portlets)


def callPageElement(self, context, request, view, name):
    pageelement = queryMultiAdapter(
        (context, request, view), IPageElement, name)

    if pageelement is None:
        return u''

    try:
        dt = datetime.now()
        rendered = pageelement.updateAndRender()
        td = datetime.now() - dt
        secs = (td.days*86400+td.seconds)+(0.000001*td.microseconds)
        print >>sys.stderr, 'pageelement:  ', '%0.6f'%secs, name
        return rendered
    except Exception, exc:
        return unicode(exc)


def renderPagelet(self, context, request, view, name):
    try:
        dt = datetime.now()
        pagelet = queryPagelet(context, request, name)
        if pagelet is not None:
             rendered = pagelet.updateAndRender()
             td = datetime.now() - dt
             secs = (td.days*86400+td.seconds)+(0.000001*td.microseconds)
             print >>sys.stderr, 'pagelet:      ', '%0.6f'%secs, name
             return rendered
    except Exception, err:
        pass

    return u''


def getitemPagelet(self, name):
    dt = datetime.now()
    view = queryPagelet(self.context, self.request, name)

    if view is not None:
        try:
            rendered = view.updateAndRender()
            td = datetime.now() - dt
            secs = (td.days*86400+td.seconds)+(0.000001*td.microseconds)
            print >>sys.stderr, 'pagelet:      ', '%0.6f'%secs, name
            return rendered
        except Exception, err:
            pass

    raise KeyError(name)


def installLogger():
    global profilerEnabled

    profilerEnabled = True
    PageletExpression.render = renderPagelet
    PageletPublisher.__getitem__ = getitemPagelet
    PortletManagerBase.render = renderPortletManager
    PageelementExpression.__call__ = callPageElement

def uninstallLogger():
    global profilerEnabled

    profilerEnabled = False
    PageletExpression.render = originalRenderPagelet
    PageletPublisher.__getitem__ = originalGetitemPagelet
    PortletManagerBase.render = originalPortletMethod
    PageelementExpression.__call__ = originalPageelementMethod
