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

$Id: fssync.py,v 1.6 2004/03/13 15:21:17 srichter Exp $
"""

from zope.fssync.server.entryadapter import DirectoryAdapter
from zope.app.site.interfaces import ISite

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
        if ISite.providedBy(self.context):
            return list(keys) + ['++etc++site']
        return keys

    def get(self, key, default=None):
        if key == '++etc++site' and ISite.providedBy(self.context):
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
        if ISite.providedBy(self.context):
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
        """Compute a folder listing.

        A folder listing is a list of the items in the folder.  It is
        a combination of the folder contents and the site-manager, if
        a folder is a site.

        The adapter will take any mapping:

        >>> adapter = FolderAdapter({'x': 1, 'y': 2})
        >>> contents = adapter.contents()
        >>> contents.sort()
        >>> contents
        [('x', 1), ('y', 2)]

        If a folder is a site, then we'll get ++etc++site included:

        >>> import zope.interface
        >>> class Site(dict):
        ...     zope.interface.implements(ISite)
        ...
        ...     def getSiteManager(self):
        ...         return 'site goes here :)'
        
        >>> adapter = FolderAdapter(Site({'x': 1, 'y': 2}))
        >>> contents = adapter.contents()
        >>> contents.sort()
        >>> contents
        [('++etc++site', 'site goes here :)'), ('x', 1), ('y', 2)]

        """
        result = super(FolderAdapter, self).contents()
        if ISite.providedBy(self.context):
            sm = self.context.getSiteManager()
            result.append(('++etc++site', sm))
        return result
