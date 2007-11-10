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

$Id: file.py 38759 2005-10-04 21:40:46Z tim_one $
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
import transaction
from zope.interface import implements
import zope.app.publication.interfaces
from zope.app.file import interfaces
from zope.app.file.file import FileChunk

from ZODB.blob import Blob

# set the size of the chunks
MAXCHUNKSIZE = 1 << 16

class File(Persistent):
    """A persistent content component storing binary file data

    Let's test the constructor:

    >>> file = File()
    >>> file.contentType
    ''
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
    >>> interfaces.IFile.implementedBy(File)
    True
    >>> verifyClass(interfaces.IFile, File)
    True
    """

    implements(zope.app.publication.interfaces.IFileContent, interfaces.IFile)

    size = 0
    
    def __init__(self, data='', contentType=''):
        self._data = Blob()
        self.contentType = contentType
        fp = self._data.open('w')
        fp.write(data)
        fp.close()

    def open(self, mode="r"):
        return self._data.open(mode)

    def _setData(self, data):
        # Handle case when data is a string
        if isinstance(data, unicode):
            data = data.encode('UTF-8')

        if isinstance(data, str):
            fp = self._data.open('w')
            fp.write(data)
            fp.close()

        if data is None:
            raise TypeError('Cannot set None data on a file.')

        # Handle case when data is already a FileChunk
        
        if isinstance(data, FileChunk):
            fp = self._data.open('w')
            chunk = data
            while chunk:
                fp.write(chunk._data)
                chunk = chunk.next
            fp.close()
            return

        # Handle case when data is a file object
        seek = data.seek
        read = data.read

        fp = self._data.open('w')
        block = data.read(MAXCHUNKSIZE)
        while block:
            fp.write(block)
        fp.close()

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
