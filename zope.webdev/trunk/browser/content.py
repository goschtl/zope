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
"""Content Component Definition/Instance Views

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.formlib import form
from zope.app import apidoc
from zope.app import zapi

from zope.webdev import interfaces, content
from zope.webdev.interfaces import _
from zope.webdev.browser import base, package

class AddForm(base.UtilityAddFormBase):

    label = _('Content Component Definition')

    form_fields = form.Fields(interfaces.IContentComponentDefinition).select(
        'name', 'schema')

    interface = interfaces.IContentComponentDefinition

    def create(self, data):
        return content.ContentComponentDefinition(**data)


class PackageOverview(object):
    """A pagelet that serves as the overview of the content component
    definitions in the package overview."""
    zope.interface.implements(package.IPackageOverviewPagelet)

    title = _('Content Component Definitions')

    def icon(self):
        return zapi.getAdapter(self.request, name='content.png')()

    def definitions(self):
        """Return PT-friendly info dictionaries for all definitions."""
        return [
            {'name': value.name,
             'schema': apidoc.utilities.getPythonPath(value.schema)}
            for value in self.context.values()
            if interfaces.IContentComponentDefinition.providedBy(value)]
