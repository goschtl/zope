##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Resource License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 40 2007-02-21 09:18:28Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
import zope.event
import zope.lifecycleevent
from zope.app.component import hooks

from z3c.sampledata.interfaces import ISampleDataPlugin
from z3c.configurator import configurator
from z3c.resource.interfaces import IResource
from z3c.website.i18n import MessageFactory as _
from z3c.website import interfaces
from z3c.website import page


class Z3CContentStructure(object):
    zope.interface.implements(ISampleDataPlugin)

    name = 'z3c.website.content'
    dependencies = ['z3c.website.site']
    schema = None

    def generate(self, context, param={}, dataSource=None, seed=None):

        # Create a virtual site
        tutorials = page.Page(u'Tutorials')
        download = page.Page(u'Download')
        contact = page.Page(u'Contact')

        # fire created event
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(tutorials))
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(download))
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(contact))

        # Add to the site
        context[u'tutorials'] = tutorials
        context[u'download'] = download
        context[u'contact'] = contact
        
        # create resources
        resource = IResource(tutorials)
        resource = IResource(download)
        resource = IResource(contact)

        # And configure the sub folders
        configurator.configure(tutorials, param)
        configurator.configure(download, param)
        configurator.configure(contact, param)
