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
from zope.schema import Choice
from zope.schema import TextLine
from zope.app import zapi
from zope.app.rdb.interfaces import IManageableZopeDatabaseAdapter

from zope.webdev.interfaces import _
from zope.webdev.browser import base, package


class AddForm(base.UtilityAddFormBase):

    label = _('Database adapter')

    form_fields = form.fields(
        TextLine(__name__='name',
            title=_("Name"),
            description=_("The name under which the utility will added and registred."),
            readonly=False,
            required=True,
            default=u''),
        Choice(__name__='factory',
            title = _(u"Database Adapter"),
            description = _(u"Select a database adapter factory."),
            required = True,
            vocabulary = "WebDev Database Adapter Factories"),
        IManageableZopeDatabaseAdapter
        ).select('name', 'dsn', 'factory')

    interface = IManageableZopeDatabaseAdapter

    def create(self, data):
        factory = data.get('factory', None)
        self.context.contentName = data.get('name', None)
        dsn = data.get('dsn', '')
        if IManageableZopeDatabaseAdapter not in factory.getInterfaces():
            raise TypeError("%s is not a IManageableZopeDatabaseAdapter" % factory)
        return factory(dsn)


class PackageOverview(object):
    """A pagelet that serves as the overview of the database adapters in the 
    package overview."""
    zope.interface.implements(package.IPackageOverviewPagelet)

    title = _('Database adapters')

    def icon(self):
        return zapi.getAdapter(self.request, name='rdb.png')()

    def definitions(self):
        """Return PT-friendly info dictionaries for all database adapters."""
        return [
            {'name': zapi.getName(value), 'dsn': value.dsn}
            for value in self.context.values()
            if IManageableZopeDatabaseAdapter.providedBy(value)]
