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

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
import time, profile
from zope.component import queryMultiAdapter
from z3ext.layoutform.interfaces import ISaveAction
from z3ext.layoutform import button, Fields, PageletEditForm
from z3ext.wizard.step import WizardStepForm
from z3ext.portlet.manager import PortletManagerBase
from z3ext.portlet.interfaces import IPortletManagerView
from z3ext.statusmessage.interfaces import IStatusMessage
from z3ext.cache import configlet as cacheconfiglet

from DMstats import Stats
from stats import ProfilerStatistics
from interfaces import IPortletProfiler


class PortletProfiler(WizardStepForm, PageletEditForm, ProfilerStatistics):

    fields = Fields(IPortletProfiler)

    buttons = PageletEditForm.buttons.copy()
    handlers = PageletEditForm.handlers.copy()

    def getStats(self):
        global _stats
        return _stats

    @button.buttonAndHandler(u'Run Profiler')
    def handleProfiler(self, action):
        configlet = self.getContent()

        installProfiler(configlet.pnumber, configlet.portlets)
        IStatusMessage(self.request).add(u'Profiler has started.')


_calls = 1
_stats = {}
_portlets = []

originalMethod = PortletManagerBase.render


def renderPortletManager(self):
    if not self.portlets or not self.isAvailable():
        return u''

    view = queryMultiAdapter((self, self.request), IPortletManagerView)
    if view is not None:
        return view.updateAndRender()

    portlets = []

    for portlet in self.portlets:
        if portlet.__name__ in _portlets:
            uri = 'portlet: %s'%portlet.__name__
            prof = profile.Profile(time.time)

            cache = cacheconfiglet.cache
            cacheconfiglet.cache = None

            response = prof.runcall(portlet.updateAndRender)

            cacheconfiglet.cache = cache

            if _stats.has_key(uri):
                _stats[uri][0].add(prof)
                _stats[uri][1] = _stats[uri][1] + 1
            else:
                _stats[uri] = ([Stats(prof), 1])

            global _calls
            if _calls > 0:
                _calls = _calls - 1

            if _calls <= 0:
                PortletManagerBase.render = originalMethod

            portlets.append(response)
        else:
            portlets.append(portlet.updateAndRender())

    return u'\n'.join(portlets)


def installProfiler(calls, portlets):
    global _calls, _stats, _portlets

    _calls = calls
    _stats = {}
    _portlets = tuple(portlets)

    PortletManagerBase.render = renderPortletManager
