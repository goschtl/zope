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
"""A site management folder contains components and component registrations.

$Id: folder.py 25177 2004-06-02 13:17:31Z jim $
"""
from zope.app.container.btree import BTreeContainer

from zope.app.component.site import SiteManagementFolder
from zope.app.component.site import SMFolderFactory

# I really hope that noone is using this.
class SiteManagementFolders(BTreeContainer):
    pass

