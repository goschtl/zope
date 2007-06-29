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
from z3c.website.i18n import MessageFactory as _
from z3c.website import interfaces
from z3c.website import site


class IWebSiteSchema(zope.interface.Interface):
    """Sample generator for a xpo site."""

    __name__ = zope.schema.TextLine(
        title=_(u'Object Name'),
        description=_(u'The name of the website.'),
        default=u"z3c",
        required=False)

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title of the website.'),
        default=u"Z3C",
        required=False)

    description = zope.schema.Text(
        title=_(u'Description'),
        description=_(u'Description of the content.'),
        default=u'',
        missing_value=u'',
        required=False)

    keyword = zope.schema.Text(
        title=_(u'Keyword'),
        description=_(u'Keyword of the content.'),
        default=u'',
        missing_value=u'',
        required=False)

    body = zope.schema.Text(
        title=_(u'Body'),
        description=_(u'Body is the main part of the page.'),
        default=u'',
        missing_value=u'',
        required=False)


class WebSite(object):
    zope.interface.implements(ISampleDataPlugin)

    name = 'z3c.website.site'
    dependencies = []
    schema = IWebSiteSchema

    def generate(self, context, param={}, dataSource={}, seed=None):

        # Create a site
        __name__ = param.get('__name__', u'z3c')
        title = param.get('title', u'Z3C')
        newSite = site.WebSite(title)
        newSite.description = param.get('description', u'')
        newSite.keyword = param.get('keyword', u'')
        newSite.body = param.get('body', u'')
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(newSite))

        # Add the site
        context[__name__] = newSite

        # Make sure the site is set correctly for handling utilities
        originalSite = hooks.getSite()
        hooks.setSite(newSite)

        # Configure the new site after adding
        param['member.login'] = 'Admin'
        param['member.password'] = u'password'
        param['member.firstName'] = u'Roger'
        param['member.lastName'] = u'Ineichen'
        param['member.phone'] = u'123'
        param['member.email'] = u'testing@projekt01.com'
        configurator.configure(newSite, param)

        # Do some cleanup
        hooks.setSite(originalSite)

        return newSite
