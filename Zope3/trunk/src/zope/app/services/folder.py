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
"""A site management folder contains components and component registrations.

$Id: folder.py,v 1.14 2003/09/21 17:32:51 jim Exp $
"""

__metaclass__ = type

from zope.app.component.nextservice import getNextServiceManager
from zope.app.container.btree import BTreeContainer
from zope.app.interfaces.services.bundle import IBundle
from zope.app.interfaces.services.folder import ISiteManagementFolders
from zope.app.interfaces.services.folder import ISiteManagementFolder
from zope.app.interfaces.services.service import IComponentManager
from zope.app.interfaces.file import IDirectoryFactory
from zope.app.services.registration import RegistrationManagerContainer
from zope.app.traversing import getPath
from zope.interface import implements
from zope.app.container.contained import setitem

class SiteManagementFolder(RegistrationManagerContainer, BTreeContainer):
    implements(ISiteManagementFolder)

class SMFolderFactory(object):

    implements(IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return SiteManagementFolder()

# XXX Backward compatability. This is needed to support old pickles.
Package = SiteManagementFolder

class SiteManagementFolders(BTreeContainer):
    pass 
Packages = SiteManagementFolders

import sys

sys.modules['zope.app.services.package'
            ] = sys.modules['zope.app.services.folder']
