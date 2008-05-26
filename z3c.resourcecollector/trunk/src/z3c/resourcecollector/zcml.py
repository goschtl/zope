##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

import zope.interface
import zope.configuration.fields
import zope.component
import zope.schema

from zope.app import zapi
from zope.app.publisher.browser import metaconfigure

from interfaces import ICollectorUtility
from browser import CollectorResource
from utility import CollectorUtility


class ICollectorDirective(zope.interface.Interface):

    name = zope.schema.TextLine(
        title=u"The name of the resource library",
        description=u"""\
        This is the name used to disambiguate resource libraries.  No two
        libraries can be active with the same name.""",
        required=True,
        )

    type = zope.configuration.fields.GlobalInterface(
        title=u"Request type",
        required=True
        )

    content_type = zope.schema.TextLine(
        title=u"Content type",
        required=False
        )


def handleCollector(_context, name, type, content_type = None):

    zapi.getGlobalSiteManager().registerUtility(CollectorUtility(content_type),name=name)
    class_=CollectorResource
    for_ = (zope.interface.Interface,)
    provides = zope.interface.Interface

    metaconfigure.resource(_context, name, layer=type, factory=class_,)


class ICollectorItemDirective(zope.interface.Interface):
    collector = zope.schema.TextLine(
        title=u"The name of the resource library",
        description=u"""\
        The name of the resourcelibrary where we want to add our resources""",
        required=True,
        )

    item = zope.schema.TextLine(
        title=u"The resource to add to the resource library",
        description=u"""\
        The resource""",
        required=True,
        )

    weight = zope.schema.Int(
        title=u"The position of the resource in the library",
        description=u"""\
        The position of the resource in the library""",
        required=True,
        )

def handleCollectorItem(_context, collector, item, weight):
    _context.action(
        discriminator = (collector, item),
        callable = addCollectorItem,
        args = (collector, item, weight)
        )

def addCollectorItem(collector, item, weight):
    rs = zope.component.getUtility(ICollectorUtility, collector)
    resource = {}
    resource['weight']=weight
    resource['resource']=item
    rs.resources[item]=resource

