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

$Id: File.py,v 1.3 2002/06/24 15:41:10 mgedmin Exp $
"""

import Persistence
from types import StringType, UnicodeType, NoneType
from FileChunk import FileChunk
from IFile import IFile

# set the size of the chunks
MAXCHUNKSIZE = 1 << 16

class File(Persistence.Persistent):
    """ """

    __implements__ = IFile

    def __init__(self, data='', contentType=None):
        """ """

        self.setData(data)

        if contentType is None:
            self._contentType = ''
        else:
            self._contentType = contentType
        

    def __len__(self):
        return self.getSize()


    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.IFile.IFile

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
        self.setData(data)


    def getData(self):
        '''See interface IFile'''
        if ( hasattr(self._data, '__class__')
         and self._data.__class__ is FileChunk ):
            return str(self._data)
        else:
            return self._data


    def setData(self, data):
        '''See interface IFile'''

        # Handle case when data is a string
        if isinstance(data, UnicodeType):
            data = data.encode('UTF-8')

        if isinstance(data, StringType):
            size = len(data)
            if size < MAXCHUNKSIZE:
                self._data, self._size = FileChunk(data), size
                return None
            self._data, self._size = FileChunk(data), size
            return None

        # Handle case when data is a string
        if isinstance(data, NoneType):
            self._data, self._size = None, 0
            return None

        # Handle case when data is already a FileChunk
        if hasattr(data, '__class__') and data.__class__ is FileChunk:
            size = len(data)
            self._data, self._size = data, size
            return None

        # Handle case when File is a file object
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
        get_transaction().commit(1)
        
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
            get_transaction().commit(1)

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

    #
    ############################################################


