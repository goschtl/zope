##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Sample generator for site generation.

Contains some general purpose generators related to site specific data.

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.event
import zope.schema
import zope.lifecycleevent
from zope.interface import implements
from zope.app.component import hooks

from zope.app.component.site import LocalSiteManager
from zope.app.folder.folder import Folder
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds

from lovely.sampledata.interfaces import ISampleDataPlugin

from lovely.sampledata import _


class ISampleSiteParameters(zope.interface.Interface):
    """The parameters for the site creation."""

    sitename = zope.schema.TextLine(
            title = _(u'Sitename'),
            required = True,
            default = u'',
            )


class SampleSite(object):

    implements(ISampleDataPlugin)

    name = 'lovely.sampledata.site'
    dependencies = []
    schema = ISampleSiteParameters

    def generate(self, context, param={}, seed=None):
        """Generate the site inside context"""
        name = param['sitename']
        folder = Folder()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(folder))
        context[name] = folder
        sm = LocalSiteManager(folder)
        folder.setSiteManager(sm)
        hooks.setSite(folder)
        return folder


class SampleIntIds(object):

    implements(ISampleDataPlugin)

    name = 'lovely.sampledata.intids'
    dependencies = []
    schema = None

    def generate(self, context, param={}, seed=None):
        """Generate an IntId utility inside context.

        'context' must be a site manager.
        """
        sm = context.getSiteManager()
        default = sm['default']

        if 'intid' not in default:
            intid = IntIds()
            zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(intid))
            default['intid'] = intid
            sm.registerUtility(intid, IIntIds)
            return intid
        else:
            return default['intid']

