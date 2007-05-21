##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 69382 2006-08-09 13:26:53Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.event
import zope.lifecycleevent
from zope.schema.fieldproperty import FieldProperty
from zope.app.container import btree
from z3c.configurator import configurator
from z3c.resource.interfaces import IResource

from z3c.website import interfaces


class Page(btree.BTreeContainer):
    """Page object."""

    zope.interface.implements(interfaces.IPage)

    title = FieldProperty(interfaces.IPage['title'])
    description = FieldProperty(interfaces.IPage['description'])
    keyword = FieldProperty(interfaces.IPage['keyword'])
    body = FieldProperty(interfaces.IPage['body'])

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class PageConfigurator(configurator.ConfigurationPluginBase):
    """Configure the page."""
    zope.component.adapts(interfaces.IPage)

    def __call__(self, data):
        # setup resource container
        IResource(self.context)
