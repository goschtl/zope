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
"""Some base classes of views.

$Id$
"""
__docformat__ = "reStructuredText"
from zope.formlib import form
from zope.app import component
from zope.app import zapi
from zope.app.pagetemplate import ViewPageTemplateFile

class UtilityAddFormBase(form.AddForm):
    """Add form for utilities."""

    # Must be provide the interface
    interface = None

    template = ViewPageTemplateFile('addform.pt')

    def add(self, object):
        object = super(UtilityAddFormBase, self).add(object)

        # Add registration
        name = zapi.getName(object)
        package = self.context.context
        registration = component.site.UtilityRegistration(
            name, self.interface, object)
        package.registrationManager.addRegistration(registration)
        registration.status = component.interfaces.registration.ActiveStatus

        return object

    def nextURL(self):
        return zapi.absoluteURL(self.context.context, self.request)
