##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This is not Free or Open Source software, but its source is made available
# when it is purchased. Please see the author(s) for details about its
# license and what you are permitted to do with its source code.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""The event handlers for the performance tests.

$Id$
"""
__docformat__ = "reStructuredText"

from zope import component

from zope.app.container.interfaces import IObjectAddedEvent

from z3c.configurator import configurator

from lovely.tag.performance.interfaces import IPerformanceTestSite


@component.adapter(IPerformanceTestSite, IObjectAddedEvent)
def onPerformanceTestSiteAdded(site,event):
    configurator.configure(site, {})

