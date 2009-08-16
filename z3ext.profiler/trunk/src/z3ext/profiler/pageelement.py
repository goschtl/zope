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
import time, profile, types
from z3ext.layoutform import button, Fields, PageletEditForm
from z3ext.wizard.step import WizardStepForm
from z3ext.pageelement.element import PageElement
from z3ext.statusmessage.interfaces import IStatusMessage

from DMstats import Stats
from stats import ProfilerStatistics
from interfaces import profilerEnabled, IPageElementProfiler


class PageElementProfiler(WizardStepForm, PageletEditForm, ProfilerStatistics):

    fields = Fields(IPageElementProfiler)

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

            installProfiler(configlet.penumber, configlet.pageelements)
            IStatusMessage(self.request).add(
                u'PageElements profiler has been started.')


_calls = 1
_stats = {}
_elements = []

originalMethod = PageElement.render


def renderPageElement(self):
    global _calls, profilerEnabled

    print self.__name__, _elements, self.__name__ in _elements

    if _calls > 0 and (self.__name__ in _elements):
        prof = profile.Profile(time.time)
        response = prof.runcall(method)

        uri = 'page element: %s'%self.__name__
        if _stats.has_key(uri):
            _stats[uri][0].add(prof)
            _stats[uri][1] = _stats[uri][1] + 1
        else:
            _stats[uri] = ([Stats(prof), 1])

        if _calls > 0:
            _calls = _calls - 1
        if _calls <= 0:
            profilerEnabled = False
            PageElement.updateAndRender = originalMethod

        return response
    else:
        return originalMethod(self)


def installProfiler(calls, elements):
    global _calls, _stats, _elements, profilerEnabled

    _calls = calls
    _stats = {}
    _elements = tuple(elements)
    profilerEnabled = True

    PageElement.render = renderPageElement
