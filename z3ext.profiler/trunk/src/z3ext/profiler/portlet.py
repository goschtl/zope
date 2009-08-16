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

from DMstats import Stats
from stats import ProfilerStatistics
from interfaces import profilerEnabled, IPortletProfiler


class PortletProfiler(WizardStepForm, PageletEditForm, ProfilerStatistics):

    fields = Fields(IPortletProfiler)

    buttons = PageletEditForm.buttons.copy()
    handlers = PageletEditForm.handlers.copy()

    def getStats(self):
        return _stats

    @button.buttonAndHandler(u'Run Profiler')
    def handleProfiler(self, action):
        if profilerEnabled:
            IStatusMessage(self.request).add(
                u'Can not start profiler. Another profiler is running.',
                'warning')
        else:
            configlet = self.getContent()

            installProfiler(configlet.pnumber, configlet.portlets)
            IStatusMessage(self.request).add(
                u'Portlets profiler has been started.')


_calls = 1
_stats = {}
_portlets = []

originalMethod = PortletManagerBase.render


def renderPortletManager(self):
    global _calls, profilerEnabled

    if not self.portlets or not self.isAvailable():
        return u''

    view = queryMultiAdapter((self, self.request), IPortletManagerView)
    if view is not None:
        return view.updateAndRender()

    portlets = []

    for portlet in self.portlets:
        if _calls > 0 and (not _portlets or portlet.__name__ in _portlets):
            prof = profile.Profile(time.time)
            response = prof.runcall(portlet.updateAndRender)

            uri = 'portlet: %s'%portlet.__name__
            if _stats.has_key(uri):
                _stats[uri][0].add(prof)
                _stats[uri][1] = _stats[uri][1] + 1
            else:
                _stats[uri] = ([Stats(prof), 1])

            if _calls > 0:
                _calls = _calls - 1
            if _calls <= 0:
                profilerEnabled = False
                PortletManagerBase.render = originalMethod

            portlets.append(response)
        else:
            portlets.append(portlet.updateAndRender())

    return u'\n'.join(portlets)


def installProfiler(calls, portlets):
    global _calls, _stats, _portlets, profilerEnabled

    _calls = calls
    _stats = {}
    _portlets = tuple(portlets)
    profilerEnabled = True

    PortletManagerBase.render = renderPortletManager
