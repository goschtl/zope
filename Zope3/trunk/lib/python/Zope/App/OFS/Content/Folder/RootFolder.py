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
from Folder import IFolder, Folder
from Zope.App.Traversing.IContainmentRoot import IContainmentRoot

class IRootFolder(IFolder, IContainmentRoot):
    """The standard Zope root Folder object interface."""


class RootFolder(Folder):
    """The standard Zope root Folder implementation."""

    __implements__ = Folder.__implements__, IRootFolder
