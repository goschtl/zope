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

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from transaction import get_transaction
from zope.interface import implements

from zope.publisher.browser import FileUpload
from interfaces import IMime, IFile, IFileContent

# set the size of the chunks
MAXCHUNKSIZE = 1 << 16

class Mime(Persistent):
    """A persistent content component storing binary file data

    Let's test the constructor:

    >>> file = Mime()
    >>> file.contentType
    ''
    >>> file.data
    ''

    >>> file = Mime('Foobar')
    >>> file.contentType
    ''
    >>> file.data
    'Foobar'

    >>> file = Mime('Foobar', 'text/plain')
    >>> file.contentType
    'text/plain'
    >>> file.data
    'Foobar'

    >>> file = Mime(data='Foobar', contentType='text/plain')
    >>> file.contentType
    'text/plain'
    >>> file.data
    'Foobar'


    Let's test the mutators:

    >>> file = Mime()
    >>> file.contentType = 'text/plain'
    >>> file.contentType
    'text/plain'

    >>> file.data = 'Foobar'
    >>> file.data
    'Foobar'

    >>> file.data = None
    Traceback (most recent call last):
    ...
    TypeError: Cannot set None data on a file.


    Let's test large data input:

    >>> file = Mime()

    Insert as string:

    >>> file.data = 'Foobar'*60000
    >>> file.getSize()
    360000
    >>> file.data == 'Foobar'*60000
    True

    Insert data as FileChunk:

    >>> fc = FileChunk('Foobar'*4000)
    >>> file.data = fc
    >>> file.getSize()
    24000
    >>> file.data == 'Foobar'*4000
    True

    Insert data from file object:

    >>> import cStringIO
    >>> sio = cStringIO.StringIO()
    >>> sio.write('Foobar'*100000)
    >>> sio.seek(0)
    >>> file.data = sio
    >>> file.getSize()
    600000
    >>> file.data == 'Foobar'*100000
    True


    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IMime.implementedBy(Mime)
    True
    >>> verifyClass(IMime, Mime)
    True
    """
    
    implements(IMime)

    def __init__(self, data='', contentType=''):
        self.data = data
        self.contentType = contentType

    def _getData(self):
        if isinstance(self._data, FileChunk):
            return str(self._data)
        else:
            return self._data

    def _setData(self, data):
        # XXX can probably be removed
        # Handle case when data is a string
        if isinstance(data, unicode):
            data = data.encode('UTF-8')

        if isinstance(data, str):
            self._data, self._size = FileChunk(data), len(data)
            return

        # Handle case when data is None
        if data is None:
            raise TypeError('Cannot set None data on a file.')

        # Handle case when data is already a FileChunk
        if isinstance(data, FileChunk):
            size = len(data)
            self._data, self._size = data, size
            return

        # Handle case when data is a file object
        seek = data.seek
        read = data.read

        seek(0, 2)
        size = end = data.tell()

        if size <= 2*MAXCHUNKSIZE:
            seek(0)
            if size < MAXCHUNKSIZE:
                self._data, self._size = read(size), size
                return
            self._data, self._size = FileChunk(read(size)), size
            return

        # Make sure we have an _p_jar, even if we are a new object, by
        # doing a sub-transaction commit.
        get_transaction().commit(1)

        jar = self._p_jar

        if jar is None:
            # Ugh
            seek(0)
            self._data, self._size = FileChunk(read(size)), size
            return

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
            jar.add(data)

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
        return

    def getSize(self):
        '''See `IFile`'''
        return self._size

    def open(self, mode='r'):
        pass

    data = property(_getData, _setData)
    

class File(Persistent):
    """
    Let's test the constructor:

    >>> file = File()
    >>> file.data
    ''

    >>> file = File('Foobar')
    >>> file.contentType
    ''
    >>> file.data
    'Foobar'

    >>> file = File('Foobar', 'text/plain')
    >>> file.contentType
    'text/plain'
    >>> file.data
    'Foobar'

    >>> file = File(data='Foobar', contentType='text/plain')
    >>> file.contentType
    'text/plain'
    >>> file.data
    'Foobar'


    Let's test the mutators:

    >>> file = File()
    >>> file.contentType = 'text/plain'
    >>> file.contentType
    'text/plain'

    >>> file.data = 'Foobar'
    >>> file.data
    'Foobar'

    >>> file.data = None
    Traceback (most recent call last):
    ...
    TypeError: Cannot set None data on a file.


    Let's test large data input:

    >>> file = File()

    Insert as string:

    >>> file.data = 'Foobar'*60000
    >>> file.getSize()
    360000
    >>> file.data == 'Foobar'*60000
    True

    Insert data as FileChunk:

    >>> fc = FileChunk('Foobar'*4000)
    >>> file.data = fc
    >>> file.getSize()
    24000
    >>> file.data == 'Foobar'*4000
    True

    Insert data from file object:

    >>> import cStringIO
    >>> sio = cStringIO.StringIO()
    >>> sio.write('Foobar'*100000)
    >>> sio.seek(0)
    >>> file.data = sio
    >>> file.getSize()
    600000
    >>> file.data == 'Foobar'*100000
    True


    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IFile.implementedBy(File)
    True
    >>> verifyClass(IFile, File)
    True
    """

    implements(IFile, IMime, IFileContent)
    
    def __init__(self, data='', contentType=''):
        self.contents = Mime()
        self.contents.data = data
        self.contentType = contentType

    # old compatibility methods
    def _getData(self):
        if isinstance(self.contents._data, FileChunk):
            # XXX here we loose our memory efficient handling
            return str(self.contents._data)
        else:
            return self.contents._data

    def _setData(self, data):
        self.contents.data = data

    def open(self, mode='r'):
        """return a file-like object for reading or updating the file value.
        """
        pass

## Leads to maximum recursion erro ?
##     # new access to file data
##     def _getContents(self):
##         return self.contents.open()

##     def _setContents(self, data):
##         self.contents = Mime()
##         contents = getattr(self, 'contents')
##         contents.data = data
##         return

##    contents = property(_getContents, _setContents)

    def getSize(self):
        return self.contents.getSize()
    
    # See IFile.
    data = property(_getData, _setData)


class FileChunk(Persistent):
    """Wrapper for possibly large data"""

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


class FileReadFile(object):
    '''Adapter for file-system style read access.

    >>> file = File()
    >>> content = "This is some file\\ncontent."
    >>> file.data = content
    >>> file.contentType = "text/plain"
    >>> FileReadFile(file).read() == content
    True
    >>> FileReadFile(file).size() == len(content)
    True
    '''
    def __init__(self, context):
        self.context = context

    def read(self):
        return self.context.data

    def size(self):
        return len(self.context.data)


class FileWriteFile(object):
    """Adapter for file-system style write access.

    >>> file = File()
    >>> content = "This is some file\\ncontent."
    >>> FileWriteFile(file).write(content)
    >>> file.data == content
    True
    """
    def __init__(self, context):
        self.context = context

    def write(self, data):
        self.context.data = data
