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
from z3c.website import sample


# TODO: add more then one site, e.g. 'org' and 'ch'
class IZ3CSamplesSchema(zope.interface.Interface):
    """Sample generator for a xpo site."""

    __name__ = zope.schema.TextLine(
        title=_(u'Object Name'),
        description=_(u'The name of the samples folder.'),
        default=u"samples",
        required=False)

    title = zope.schema.TextLine(
        title=_(u'Title'),
        description=_(u'The title of the samples folder.'),
        default=u"Samples",
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


class Z3CSamples(object):
    zope.interface.implements(ISampleDataPlugin)

    name = 'z3c.website.samples'
    dependencies = ['z3c.website.site']
    schema = IZ3CSamplesSchema

    def generate(self, context, param={}, dataSource=None, seed=None):

        # Create a virtual site
        title = param.get('title', u'Samples')
        __name__ = param.get('__name__', u'samples')
        obj = sample.Samples(title)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))

        # Add the site
        context[__name__] = obj

        # Configure the new site after adding
        configurator.configure(obj, param)

        return obj