##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Page Folders

Page folders support easy creation and registration of page views
using folders of templates.

$Id: pagefolder.py,v 1.16 2003/11/21 17:10:01 jim Exp $
"""
__metaclass__ = type

from zope.app.container.btree import BTreeContainer
from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.registration import IRegistrationManager
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.services.presentation import PageRegistration
from zope.app.services.registration import RegistrationManagerContainer
from zope.app.services.zpt import IZPTTemplate
from zope.app.traversing import getPath
from zope.app.traversing import getPath
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.proxy import removeAllProxies
from zope.publisher.interfaces.browser import IBrowserRequest

import zope.app.component.interfacefield
import zope.app.interfaces.container
import zope.app.interfaces.file
import zope.app.interfaces.fssync
import zope.app.interfaces.services.registration
import zope.app.security.permission
import zope.interface
import zope.schema

class IPageFolderInfo(zope.interface.Interface):
    """Default registration information for page folders

    This information is used to configure the pages in the folder.
    """

    required = zope.app.component.interfacefield.InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being viewed",
        required = True,
        )

    factoryName = zope.schema.BytesLine(
        title=u"The dotted name of a factory for creating the view",
        required = False,
        )

    layer = zope.schema.BytesLine(
        title = u"Layer",
        description = u"The skin layer the view is registered for",
        required = False,
        min_length = 1,
        default = "default",
        )

    permission = zope.app.security.permission.PermissionField(
        title=u"Permission",
        description=u"The permission required to use the view",
        required = True,
        )

    apply = zope.schema.Bool(
        title=u"Apply changes to existing pages",
        required = True,
        )

class IPageFolder(
    IPageFolderInfo,
    zope.app.interfaces.container.IContainer,
    zope.app.interfaces.services.registration.IRegistrationManagerContainer,
    ):

    def applyDefaults(self):
        """Apply the default configuration to the already-registered pages. 
        """

class PageFolder(RegistrationManagerContainer, BTreeContainer):

    zope.interface.implements(IPageFolder)

    requestType = IBrowserRequest
    layer = "default"
    description = ''
    title = ''
    factoryName = None
    attribute = None
    template = None
    apply = True

    ########################################################
    # The logic for managing registrations is handled by the
    # decorator class below.
    ########################################################


    def __setitem__(self, name, object):
        if (IRegistrationManager.isImplementedBy(object) or
            IZPTTemplate.isImplementedBy(object)):
            super(PageFolder, self).__setitem__(name, object)
        else:
            raise TypeError("Can only add templates", object)


        # If a template is added, we need to configure it too.
        if IZPTTemplate.isImplementedBy(object):
            template = self[name]
            template = getPath(template)
            registration = PageRegistration(
                required=self.required,
                name=name,
                permission=self.permission,
                factoryName=self.factoryName,
                template=template,
                layer=self.layer,
                )

            registrations = self.getRegistrationManager()
            id = registrations.addRegistration(registration)
            registration = registrations[id]
            registration.status = ActiveStatus

    def applyDefaults(self):
        """Apply the default configuration to the already-registered pages.
        """

        rm = self.getRegistrationManager()
        for name in rm:
            registration = rm[name]
            status = registration.status
            if status == ActiveStatus:
                registration.status = RegisteredStatus
            registration.status = UnregisteredStatus

            # Cheat and set required and layer even though they're
            # read-only.  This is ok since the registration is now not
            # registered.

            registration.required = removeAllProxies(self.required)
            registration.factoryName = self.factoryName
            registration.layer = self.layer
            registration.permission = self.permission

            # Now restore the registration status

            registration.status = status


_attrNames = (
    'factoryName',
    'required',
    'layer',
    'permission',
    )

class PageFolderAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for PageFolder objects."""

    zope.interface.implements(zope.app.interfaces.fssync.IObjectDirectory)

    def contents(self):
        return self.context.items()

    def extra(self):
        return AttrMapping(self.context, _attrNames)


class PageFolderFactory:

    zope.interface.implements(zope.app.interfaces.file.IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return PageFolder()


# XXX Backward compatibility. This is needed to support old pickles.
ViewPackage = PageFolder
import sys
sys.modules['zope.app.services.viewpackage'
            ] = sys.modules['zope.app.services.pagefolder']
