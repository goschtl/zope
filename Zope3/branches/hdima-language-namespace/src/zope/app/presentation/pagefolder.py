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
"""Page Folders

Page folders support easy creation and registration of page views
using folders of templates.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface, implements
from zope.proxy import removeAllProxies
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.app import zapi
from zope.app.component.interfaces.registration import ActiveStatus
from zope.app.component.interfaces.registration import InactiveStatus
from zope.app.component.interfaces.registration import IRegistered
from zope.app.component.registration import RegisterableContainer
from zope.app.container.btree import BTreeContainer
from zope.app.filerepresentation.interfaces import IDirectoryFactory

import interfaces
import registration

class PageFolder(RegisterableContainer, BTreeContainer):

    implements(interfaces.IPageFolder)

    requestType = IBrowserRequest
    layer = "default"
    description = ''
    title = ''
    factoryName = None
    attribute = None
    template = None
    apply = True

    def applyDefaults(self):
        """Apply the default configuration to the already-registered pages."""

        for name in self.registrationManager:
            registration = self.registrationManager[name]
            orig_status = registration.status
            registration.status = InactiveStatus

            # Cheat and set required even though it is read-only. This is ok
            # since the registration is now not registered.

            registration.required = removeAllProxies(self.required)
            registration.factoryName = self.factoryName
            registration.permission = self.permission

            # Now restore the registration status

            registration.status = orig_status


def templateAddedSubscriber(template, event):
    """Create a registration for the added template."""
    pagefolder = zapi.getParent(template)
    # Create and add template 
    reg = registration.PageRegistration(
        required=pagefolder.required,
        name=zapi.name(template),
        permission=pagefolder.permission,
        factoryName=pagefolder.factoryName,
        template=template,
        )
    
    id = pagefolder.registrationManager.addRegistration(reg)
    reg.status = ActiveStatus


def templateRemovedSubscriber(template, event):
    """Remove the registration of a template, when it is removed."""
    registered = IRegistered(template)
    reg_manager = zapi.getParent(template.registrationManager)
    for reg in registered.registrations():
        del reg_manager[zapi.name(reg)]


class PageFolderFactory(object):
    """A directory factory to create page folders inside site
    management folders.
    """

    implements(IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return PageFolder()

