##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.component
import zope.schema
from zope.schema.fieldproperty import FieldProperty
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.component.interfaces import IPossibleSite
from zope.site import folder
from zope.app.component import site

from z3c.baseregistry import baseregistry

from zam.api.i18n import MessageFactory as _
from zam.api import plugin

###############################################################################
#
# ZAM test site used in different zam package tests
#
###############################################################################

class IZAMTestSite(IPossibleSite, IAttributeAnnotatable):
    """ZAM test site interface."""

    __name__ = zope.schema.TextLine(
        title=_('Object name.'),
        description=_('The object name.'),
        default=u'ZAMDemoSite',
        missing_value=u'',
        required=True)

    title = zope.schema.TextLine(
        title=_('Title'),
        description=_('The title of the demo site.'),
        default=u'',
        missing_value=u'',
        required=True)


class ZAMTestSite(folder.Folder):
    """ZAM test site."""

    zope.interface.implements(IZAMTestSite)

    title = FieldProperty(IZAMTestSite['title'])

    def __init__(self, title):
        super(ZAMTestSite, self).__init__()
        self.title = title

        # setup site manager
        self.setSiteManager(site.LocalSiteManager(self))

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


ZAMTestBaseRegistry = baseregistry.BaseComponents(
    zope.component.globalSiteManager, 'zam.api.testing')


class ZAMTestPlugin(plugin.BaseRegistryPlugin):
    """ZAM test plugin."""

    registry = ZAMTestBaseRegistry

    title = _("ZAM test plugin")

    description = _("ZAM test plugin.")

    def install(self, site):
        super(ZAMTestPlugin, self).install(site)
        setattr(site, 'testAttr', 'dummy')

    def uninstall(self, site):
        super(ZAMTestPlugin, self).uninstall(site)
        delattr(site, 'testAttr')


