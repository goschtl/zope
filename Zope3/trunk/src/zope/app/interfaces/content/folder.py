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
"""

$Id: folder.py,v 1.3 2002/12/28 14:13:25 stevea Exp $
"""

from zope.app.interfaces.container import IAdding
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.services.service import IServiceManagerContainer

class IFolder(IContainer, IServiceManagerContainer):
    """The standard Zope Folder object interface."""

class IRootFolder(IFolder, IContainmentRoot):
    """The standard Zope root Folder object interface."""

class IFolderAdding(IAdding):
    pass
