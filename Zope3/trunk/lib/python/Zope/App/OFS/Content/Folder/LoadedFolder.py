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
Revision information: 
$Id: LoadedFolder.py,v 1.2 2002/06/10 23:28:00 jim Exp $

Implemented LoadedFolder Functionality:

- Order Folder items
- Define a max amount of items possible

Todo Functionality:

- Define what content objects can be added (user)
  + add the option to the configuration zpt
  + how does the security work for this? like if this folder is
    created under a folder that doesnt allow images for example?
    so need to figure out how to get a list of "allowed" content
    objects.  also, will what can be added to this folder be
    static or dynamic in the sence of if security settings change
    will this folder know about it?
"""

from Folder import Folder, IFolder
from FolderLimit import FolderLimit, FolderLimitExceededError
from OrderedFolder import OrderedFolder
from types import StringTypes

from Zope.App.OFS.Container.Exceptions import UnaddableError

class ILoadedFolder(IFolder):
    """The standard Zope Loaded Folder object interface."""

class LoadedFolder(Folder, FolderLimit, OrderedFolder):
    """Implements some nice additional features to the regular
       Folder.
    """

    __implements__ = (ILoadedFolder, Folder.__implements__,
                      FolderLimit.__implements__, OrderedFolder.__implements__)


    # XXX Reimplementation of some of the IReadContainer API. Shrug.
    
    def keys(self):
        """Return a sequence-like object containing the names 
           associated with the objects that appear in the folder
        """
        return self._orderedIds


    def values(self):
        """Return a sequence-like object containing the objects that
           appear in the folder.
        """
        result = []
        for id in self.keys():
            result.append(self.data[id])

        return tuple(result)


    def items(self):
        """Return a sequence-like object containing tuples of the form
           (name, object) for the objects that appear in the folder.
        """
        result = []
        for id in self.keys():
            result.append((id, self.data[id]))

        return result


    # XXX Reimplementation of some of the IWriteContainer API. Shrug again.

    def setObject(self, name, object):
        """Add the given object to the folder under the given name."""
        if type(name) in StringTypes and len(name)==0:
            raise ValueError
        if self.isLimitReached():
            raise FolderLimitExceededError(self, object,
                       'The folder\'s limit (%d item%s) was exeeded.' %
                       (self.getLimit(), self.getLimit()==1 and "" or "s" ))
        else:
            self.data[name] = object
            if name not in self._orderedIds:
                self._orderedIds += (name,)

        return name

    def __delitem__(self, name):
        """Delete the named object from the folder. Raises a KeyError
           if the object is not found."""
        del self.data[name]
        ids = list(self._orderedIds)
        ids.remove(name)
        self._orderedIds = tuple(ids)
