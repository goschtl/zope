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
import datetime
import pytz

import zope.interface
import zope.app.component.interfaces.registration
from zope.formlib import form
from zope.app import zapi
from zope.app import apidoc
from zope.webdev import interfaces, resourcecontainer
from zope.webdev.browser import base, package
from zope.webdev.interfaces import _
from zope.webdev.resourcecontainer import registerResourceDirectory
from zope.security.proxy import removeSecurityProxy
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.interface.common import idatetime


class AddForm(base.UtilityAddFormBase):

    label = _('ResourceContainer')

    form_fields = form.Fields(interfaces.IResourceContainer).select(
        'name', 'permission', 'layers')

    interface = interfaces.IResourceContainer

    def create(self, data):
        return resourcecontainer.ResourceContainer(**data)

    def add(self, obj):
        obj = super(form.AddForm, self).add(obj)
        obj=removeSecurityProxy(obj)
        registerResourceDirectory(obj)
        return obj


class PackageOverview(object):
    """A pagelet that serves as the overview of resource containers in
    the package overview."""
    zope.interface.implements(package.IPackageOverviewPagelet)

    title = _("ResourceContainers")

    def icon(self):
        return zapi.getAdapter(self.request, name='resourcecontainer.png')()

    def containers(self):
        """Return PT-friendly info dictionaries for all containers."""
        containers = []
        for container in self.context.values():
            if interfaces.IResourceContainer.providedBy(container):
                containers.append({
                    'name': container.name,
                    'absolute_url': zapi.getView(container, 'absolute_url', self.request)(),
                    })

        return containers


class Overview(base.EditFormBase):
    """ResourceContainer Overview."""
    form_fields = form.Fields(interfaces.IResourceContainer).select(
        'name', 'permission', 'layers')
    template = ViewPageTemplateFile('package_overview.pt')
