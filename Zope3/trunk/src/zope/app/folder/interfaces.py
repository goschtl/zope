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
"""Folder interfaces

$Id: interfaces.py,v 1.3 2004/03/03 10:38:43 philikon Exp $
"""
from zope.app.container.interfaces import IAdding
from zope.app.container.interfaces import IContainer, IContentContainer
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.services.service import IPossibleSite
from zope.app.interfaces.annotation import IAttributeAnnotatable

class IFolder(IContainer, IContentContainer, IPossibleSite,
              IAttributeAnnotatable):
    """The standard Zope Folder object interface."""

class IRootFolder(IFolder, IContainmentRoot):
    """The standard Zope root Folder object interface."""

class IFolderAdding(IAdding):
    pass
