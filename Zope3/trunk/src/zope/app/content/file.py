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

$Id: file.py,v 1.5 2003/02/03 15:08:32 jim Exp $
"""
import datetime
zerotime = datetime.datetime.fromtimestamp(0)

from persistence import Persistent
from transaction import get_transaction

from zope.component import getAdapter
from zope.publisher.browser import FileUpload

from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.content.file import IFile, IReadFile

# set the size of the chunks
MAXCHUNKSIZE = 1 << 16

class File(Persistent):
    __implements__ = IFile

    def __init__(self, data='', contentType=''):
        self.data = data
        self.contentType = contentType


    def __len__(self):
        return self.size


    def setContentType(self, contentType):
        '''See interface IFile'''
        self._contentType = contentType


    def getContentType(self):
        '''See interface IFile'''
        return self._contentType


    def edit(self, data, contentType=None):
        '''See interface IFile'''
        # XXX This seems broken to me, as setData can override the
        # content type explicitly passed in.

        if contentType is not None:
            self._contentType = contentType
        if hasattr(data, '__class__') and data.__class__ is FileUpload \
           and not data.filename:
            data = None          # Ignore empty files
        if data is not None:
            self.data = data


    def getData(self):
        '''See interface IFile'''
        if hasattr(self._data, '__class__') and \
           self._data.__class__ is FileChunk:
            return str(self._data)
        else:
            return self._data


    def setData(self, data):
        '''See interface IFile'''
        # Handle case when data is a string
        if isinstance(data, unicode):
            data = data.encode('UTF-8')

        if isinstance(data, str):
            size = len(data)
            if size < MAXCHUNKSIZE:
                self._data, self._size = FileChunk(data), size
                return None
            self._data, self._size = FileChunk(data), size
            return None

        # Handle case when data is None
        if data is None:
            self._data, self._size = None, 0
            return None

        # Handle case when data is already a FileChunk
        if hasattr(data, '__class__') and data.__class__ is FileChunk:
            size = len(data)
            self._data, self._size = data, size
            return None

        # Handle case when data is a file object
        seek = data.seek
        read = data.read

        seek(0, 2)
        size = end = data.tell()

        if size <= 2*MAXCHUNKSIZE:
            seek(0)
            if size < MAXCHUNKSIZE:
                self._data, self._size = read(size), size
                return None
            self._data, self._size = FileChunk(read(size)), size
            return None

        # Make sure we have an _p_jar, even if we are a new object, by
        # doing a sub-transaction commit.
        get_transaction().savepoint()

        jar = self._p_jar

        if jar is None:
            # Ugh
            seek(0)
            self._data, self._size = FileChunk(read(size)), size
            return None

        # Now we're going to build a linked list from back
        # to front to minimize the number of database updates
        # and to allow us to get things out of memory as soon as
        # possible.
        next = None
        while end > 0:
            pos = end - MAXCHUNKSIZE
            if pos < MAXCHUNKSIZE:
                pos = 0 # we always want at least MAXCHUNKSIZE bytes
            seek(pos)
            data = FileChunk(read(end - pos))

            # Woooop Woooop Woooop! This is a trick.
            # We stuff the data directly into our jar to reduce the
            # number of updates necessary.
            data._p_jar = jar

            # This is needed and has side benefit of getting
            # the thing registered:
            data.next = next

            # Now make it get saved in a sub-transaction!
            get_transaction().savepoint()

            # Now make it a ghost to free the memory.  We
            # don't need it anymore!
            data._p_changed = None

            next = data
            end = pos

        self._data, self._size = next, size
        return None


    def getSize(self):
        '''See interface IFile'''
        return self._size

    data = property(getData, setData, None,
                    """Contains the data of the file.""")

    contentType = property(getContentType, setContentType, None,
                           """Specifies the content type of the data.""")

    size = property(getSize, None, None,
                    """Specifies the size of the file in bytes. Read only.""")


# Adapter for ISearchableText

from zope.app.interfaces.index.text import ISearchableText

class SearchableText:

    __implements__ = ISearchableText
    __used_for__ = IReadFile

    def __init__(self, file):
        self.file = file

    def getSearchableText(self):
        if self.file.contentType == "text/plain":
            return [unicode(self.file.data)]
        else:
            return None


class FileChunk(Persistent):
    # Wrapper for possibly large data

    next = None

    def __init__(self, data):
        self._data = data


    def __getslice__(self, i, j):
        return self._data[i:j]


    def __len__(self):
        data = str(self)
        return len(data)


    def __str__(self):
        next = self.next
        if next is None:
            return self._data

        result = [self._data]
        while next is not None:
            self = next
            result.append(self._data)
            next = self.next

        return ''.join(result)

# Adapters for file-system style access

class FileReadFile:

    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.getData()

    def size(self):
        return len(self.context.getData())

class FileWriteFile:

    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context.setData(data)
