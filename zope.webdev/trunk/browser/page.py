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
"""Schema Views

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.formlib import form
from zope.app import zapi
from zope.app import apidoc

from zope.webdev import interfaces, page
from zope.webdev.browser import base, package
from zope.webdev.interfaces import _

class AddForm(base.UtilityAddFormBase):

    label = _('Page')

    form_fields = form.Fields(interfaces.IPage).select(
        'name', 'for_')

    interface = interfaces.IPage

    def create(self, data):
        return page.Page(**data)


class PackageOverview(object):
    """A pagelet that serves as the overview of pages in the package
    overview."""
    zope.interface.implements(package.IPackageOverviewPagelet)

    title = _("Pages")

    def icon(self):
        return zapi.getAdapter(self.request, name='page.png')()

    def pages(self):
        """Return PT-friendly info dictionaries for all pages."""
        pages = []
        for page in self.context.values():
            if interfaces.IPage.providedBy(page):
                pages.append(
                    {'name': page.name,
                     'for':  apidoc.utilities.getPythonPath(page.for_)})

        return pages
