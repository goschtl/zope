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


class IRootFolder(IFolder):
    """The standard Zope root Folder object interface."""


class RootFolder(Folder):
    """The standard Zope root Folder implementation."""

    __implements__ = Folder.__implements__, IRootFolder

    def __call__(self):
        return 'You have reached the wrong number (but the right ' \
               'object!). Please try again later.'
