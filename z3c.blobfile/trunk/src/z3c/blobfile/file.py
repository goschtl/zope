##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""File content component

TODO: 
- we should rename `_data` to `_blob` in `File`
- should we then keep `_data` in `File` for backwards compatibility?
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
import transaction
from zope.interface import implements
import zope.component
import zope.app.publication.interfaces
import zope.app.file.interfaces

from ZODB.blob import Blob

import interfaces

# set the size of the chunks
MAXCHUNKSIZE = 1 << 16

class File(Persistent):
    """A persistent content component storing binary file data."""

    implements(zope.app.publication.interfaces.IFileContent, 
               zope.app.file.interfaces.IFile)

    size = 0
    
    def __init__(self, data='', contentType=''):
        self._data = Blob()
        self.contentType = contentType
        self._setData(data)

    def open(self, mode="r"):
        return self._data.open(mode)

    def _setData(self, data):
        # Search for a storable that is able to store the data
        dottedName = ".".join((data.__class__.__module__,
                               data.__class__.__name__))
        storable = zope.component.getUtility(interfaces.IStorage, 
                                             name=dottedName)
        storable.store(data, self._data)

    def _getData(self):
        fp = self._data.open('r')
        data = fp.read()
        fp.close()
        return data

    data = property(_getData, _setData)    

    @property
    def size(self):
        if self._data == "":
            return 0
        reader = self._data.open()
        reader.seek(0,2)
        size = int(reader.tell())
        reader.close()
        return size

    def getSize(self):
        return self.size

class FileReadFile(object):
    """Adapter for file-system style read access."""
    
    def __init__(self, context):
        self.context = context

    def read(self, bytes=-1):
        return self.context.data

    def size(self):
        return self.context.size


class FileWriteFile(object):
    """Adapter for file-system style write access."""
    
    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context._setData(data)
