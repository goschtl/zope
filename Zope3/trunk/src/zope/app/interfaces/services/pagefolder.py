##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Page Folder interfaces

Page folders support easy creation and registration of page views
using folders of templates.

$Id: pagefolder.py,v 1.4 2003/06/21 21:22:10 jim Exp $
"""
from zope.app.component.interfacefield import InterfaceField
from zope.schema import BytesLine
from zope.app.interfaces.container import IContainer
from zope.app.security.permission import PermissionField
from zope.app.interfaces.services.registration \
     import IRegistrationManagerContainer
from zope.interface import Interface

class IPageFolderInfo(Interface):
    """Default registration information for page folders

    This information is used to configure the pages in the folder.
    """

    forInterface = InterfaceField(
        title = u"For interface",
        description = u"The interface of the objects being viewed",
        required = True,
        )

    factoryName = BytesLine(
        title=u"The dotted name of a factory for creating the view",
        required = True,
        )

    layer = BytesLine(
        title = u"Layer",
        description = u"The skin layer the view is registered for",
        required = False,
        min_length = 1,
        default = "default",
        )

    permission = PermissionField(
        title=u"Permission",
        description=u"The permission required to use the view",
        required = True,
        )

class IPageFolder(IPageFolderInfo,
                  IContainer,
                  IRegistrationManagerContainer):
    """Sub-packages that contain templates that are registered as page views
    """
