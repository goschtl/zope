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
"""The performance site configurator.

$Id$
"""
__docformat__ = "reStructuredText"

from zope import component
from zope import event
from zope.lifecycleevent import ObjectCreatedEvent

from zope.app.component import hooks
from zope.app.component.interfaces import ISite
from zope.app.component.site import LocalSiteManager
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds

from z3c.configurator import configurator

from lovely import tag

from lovely.tag.performance.interfaces import IPerformanceTestSite


class SetUpPerformanceTestSite(configurator.ConfigurationPluginBase):
    component.adapts(IPerformanceTestSite)

    def __call__(self, data):
        if not ISite.providedBy(self.context):
            sm = LocalSiteManager(self.context)
            self.context.setSiteManager(sm)
        else:
            sm = self.context.getSiteManager()
        hooks.setSite(self.context)

        default = sm['default']

        if 'intid' not in default:
            intid = IntIds()
            event.notify(ObjectCreatedEvent(intid))
            default['intid'] = intid
            sm.registerUtility(intid, IIntIds)

        # Add the tagging engine
        if 'tagging-engine' not in default:
            engine = tag.TaggingEngine()
            event.notify(ObjectCreatedEvent(engine))
            default['tagging-engine'] = engine
            sm.registerUtility(engine, tag.interfaces.ITaggingEngine)

