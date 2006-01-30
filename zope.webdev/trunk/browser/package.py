##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Package Browser Code.

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
import zope.app.event.objectevent
from zope import viewlet
from zope.formlib import form
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.webdev import interfaces
from zope.webdev.browser import pagelet, base

class Overview(base.EditFormBase):
    """Package Overview."""

    form_fields = form.Fields(interfaces.IPackage).select(
        'docstring', 'version', 'license', 'author')
    template = ViewPageTemplateFile('package_overview.pt')

    def fixUpWidgets(self):
        self.widgets.get('docstring').height = 3


class IPackageOverviewManager(pagelet.IPageletManager):
    """A pagelet manager to display contents of a package."""


class IPackageOverviewPagelet(pagelet.IPagelet):
    """A pagelet that is displayed in the package overview pagelet manager."""

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the pagelet.',
        required=True)


class PackageOverviewManager(pagelet.PageletManagerBase,
                             viewlet.manager.ViewletManagerBase):
    """Ordered pagelet manager."""
    zope.interface.implements(IPackageOverviewManager)

    def sort(self, viewlets):
        """Sort the viewlets on their weight."""
        return sorted(viewlets,
                      lambda x, y: cmp(int(x[1].weight), int(y[1].weight)))
