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

from persistence import Persistent
from zodb.btrees.OOBTree import OOBTree
from zope.app.interfaces.content.folder import IFolder, IRootFolder
from zope.app.services.servicecontainer import ServiceManagerContainer
from zope.app.interfaces.services.service import IServiceManagerContainer
from zope.exceptions import DuplicationError


class Folder(Persistent, ServiceManagerContainer):
    """The standard Zope Folder implementation."""

    __implements__ = IFolder

    def __init__(self):
        self.data = OOBTree()

    def keys(self):
        """Return a sequence-like object containing the names
           associated with the objects that appear in the folder
        """
        return self.data.keys()

    def __iter__(self):
        return iter(self.data.keys())

    def values(self):
        """Return a sequence-like object containing the objects that
           appear in the folder.
        """
        return self.data.values()

    def items(self):
        """Return a sequence-like object containing tuples of the form
           (name, object) for the objects that appear in the folder.
        """
        return self.data.items()

    def __getitem__(self, name):
        """Return the named object, or the value of the default
           argument if given and the named object is not found.
           If no default is given and the object is not found a
           KeyError is raised.
        """
        return self.data[name]

    def get(self, name, default=None):
        """Return the named object, or the value of the default
           argument if given and the named object is not found.
           If no default is given and the object is not found a
           KeyError is raised.
        """
        return self.data.get(name, default)

    def __contains__(self, name):
        """Return true if the named object appears in the folder."""
        return self.data.has_key(name)

    def __len__(self):
        """Return the number of objects in the folder."""
        return len(self.data)

    def setObject(self, name, object):
        """Add the given object to the folder under the given name."""

        if not (isinstance(name, str) or isinstance(name, unicode)):
            raise TypeError("Name must be a string rather than a %s" %
                            name.__class__.__name__)
        try:
            unicode(name)
        except UnicodeError:
            raise TypeError("Non-unicode names must be 7-bit-ascii only")
        if not name:
            raise TypeError("Name must not be empty")

        if name in self.data:
            raise DuplicationError("name, %s, is already in use" % name)

        self.data[name] = object
        return name

    def __delitem__(self, name):
        """Delete the named object from the folder. Raises a KeyError
           if the object is not found."""
        del self.data[name]


class RootFolder(Folder):
    """The standard Zope root Folder implementation."""

    __implements__ = Folder.__implements__, IRootFolder


# Adapter to provide a file-system rendition of folders

class ReadDirectory:

    def __init__(self, context):
        self.context = context

    def keys(self):
        keys = self.context.keys()
        if self.context.hasServiceManager():
            return list(keys) + ['++etc++Services']
        return keys

    def get(self, key, default=None):
        if key == '++etc++Services' and self.context.hasServiceManager():
            return self.context.getServiceManager()

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
        if self.context.hasServiceManager():
            l += 1
        return l

    def items(self):
        get = self.get
        return [(key, get(key)) for key in self.keys()]

    def __contains__(self, key):
        return self.get(key) is not None  
    

