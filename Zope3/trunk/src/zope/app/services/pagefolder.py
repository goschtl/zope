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

$Id: pagefolder.py,v 1.15 2003/11/04 04:04:25 jeremy Exp $
"""
__metaclass__ = type

from zope.app.container.btree import BTreeContainer
from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.app.interfaces.file import IDirectoryFactory
from zope.app.interfaces.fssync import IObjectDirectory
from zope.app.interfaces.services.pagefolder import IPageFolder
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.registration import IRegistrationManager
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.interfaces.services.view import IZPTTemplate
from zope.app.services.registration import RegistrationManagerContainer
from zope.app.services.view import PageRegistration
from zope.app.traversing import getPath
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.publisher.interfaces.browser import IBrowserPresentation

class PageFolder(RegistrationManagerContainer, BTreeContainer):

    implements(IPageFolder)

    presentationType = IBrowserPresentation
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
                forInterface=self.forInterface,
                viewName=name,
                permission=self.permission,
                class_=self.factoryName,
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

            # Cheat and set forInterface and layer even though they're
            # read-only.  This is ok since the registration is now not
            # registered.

            registration.forInterface = removeAllProxies(self.forInterface)
            registration.factoryName = self.factoryName
            registration.layer = self.layer
            registration.permission = self.permission

            # Now restore the registration status

            registration.status = status


_attrNames = (
    'factoryName',
    'forInterface',
    'layer',
    'permission',
    )

class PageFolderAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for PageFolder objects."""

    implements(IObjectDirectory)

    def contents(self):
        return self.context.items()

    def extra(self):
        return AttrMapping(self.context, _attrNames)


class PageFolderFactory:

    implements(IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return PageFolder()


# XXX Backward compatibility. This is needed to support old pickles.
ViewPackage = PageFolder
import sys
sys.modules['zope.app.services.viewpackage'
            ] = sys.modules['zope.app.services.pagefolder']
