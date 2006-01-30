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

from zope.webdev import interfaces, schema
from zope.webdev.browser import base, package
from zope.webdev.interfaces import _

class AddForm(base.UtilityAddFormBase):

    label = _('Schema')

    form_fields = form.Fields(interfaces.ISchema).select(
        'name', 'docstring', 'bases')

    interface = interfaces.ISchema

    def create(self, data):
        return schema.Schema(**data)


class PackageOverview(object):
    """A pagelet that serves as the overview of schemas in the package
    overview."""
    zope.interface.implements(package.IPackageOverviewPagelet)

    title = _('Schemas')

    def icon(self):
        return zapi.getAdapter(self.request, name='schema.png')()

    def schemas(self):
        """Return PT-friendly info dictionaries for all schemas."""
        schemas = []
        for schema in self.context.values():
            if interfaces.ISchema.providedBy(schema):
                fields = [
                    {'name': name,
                     'type': field.__class__.__name__}
                    for name, field in schema.namesAndDescriptions()]
                schemas.append(
                    {'name': schema.name,
                     'bases': [base.getName() for base in schema.getBases()],
                     'fields': fields})

        return schemas
