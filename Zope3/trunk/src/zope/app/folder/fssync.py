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
"""Filesystem synchronization support.

$Id: fssync.py,v 1.2 2004/02/24 16:49:59 philikon Exp $
"""

from zope.interface import implements
from zope.fssync.server.entryadapter import ObjectEntryAdapter, \
     DirectoryAdapter, AttrMapping
from zope.fssync.server.interfaces import IContentDirectory

__metaclass__ = type

class RootDirectoryFactory:

    def __init__(self, context):
        pass

    def __call__(self, name):
        return Folder()

class ReadDirectory:
    """Adapter to provide a file-system rendition of folders
    """

    def __init__(self, context):
        self.context = context

    def keys(self):
        keys = self.context.keys()
        if ISite.isImplementedBy(self.context):
            return list(keys) + ['++etc++site']
        return keys

    def get(self, key, default=None):
        if key == '++etc++site' and ISite.isImplementedBy(self.context):
            return self.context.getSiteManager()

        return self.context.get(key, default)

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, key):
        v = self.get(key, self)
        if v is self:
            raise KeyError, key
        return v

    def values(self):
        return map(self.get, self.keys())

    def __len__(self):
        l = len(self.context)
        if ISite.isImplementedBy(self.context):
            l += 1
        return l

    def items(self):
        get = self.get
        return [(key, get(key)) for key in self.keys()]

    def __contains__(self, key):
        return self.get(key) is not None

class FolderAdapter(DirectoryAdapter):
    """Adapter to provide an fssync interpretation of folders
    """

    def contents(self):
        result = super(FolderAdapter, self).contents()
        if ISite.isImplementedBy(self.context):
            sm = self.context.getSiteManager()
            result.append(('++etc++site', sm))
        return result
