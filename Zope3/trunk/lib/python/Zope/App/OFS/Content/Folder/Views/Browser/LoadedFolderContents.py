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
"""
    Define view component for loaded folder contents.

$Id: LoadedFolderContents.py,v 1.2 2002/06/10 23:28:00 jim Exp $
"""

from Zope.App.PageTemplate import ViewPageTemplateFile
from FolderContents import FolderContents


class LoadedFolderContents( FolderContents ):

    index = ViewPageTemplateFile( 'loaded_folder_contents.pt' )


    # OrderedFolder functionality

    def moveObjectsUp(self, ids, REQUEST = None):
        '''See interface IOrderedContainer'''
        self.context.moveObjectsUp(ids)

        if REQUEST is not None:
            # for unit tests
            REQUEST.getResponse().redirect(REQUEST.getURL(1))


    def moveObjectsDown(self, ids, REQUEST = None):
        '''See interface IOrderedContainer'''
        self.context.moveObjectsDown(ids)

        if REQUEST is not None:
            # for unit tests
            REQUEST.getResponse().redirect(REQUEST.getURL(1))


    def moveObjectsToTop(self, ids, REQUEST = None):
        '''See interface IOrderedContainer'''
        self.context.moveObjectsToTop(ids)

        if REQUEST is not None:
            # for unit tests
            REQUEST.getResponse().redirect(REQUEST.getURL(1))


    def moveObjectsToBottom(self, ids, REQUEST = None):
        '''See interface IOrderedContainer'''
        self.context.moveObjectsToBottom(ids)

        if REQUEST is not None:
            # for unit tests
            REQUEST.getResponse().redirect(REQUEST.getURL(1))


