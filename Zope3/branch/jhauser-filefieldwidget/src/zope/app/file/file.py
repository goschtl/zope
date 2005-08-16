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

from warnings import warn
from persistent import Persistent
from transaction import get_transaction

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from zope.publisher.browser import FileUpload
from zope.security.proxy import removeSecurityProxy

from zope.app.file.interfaces import IReadFileStorage, IWriteFileStorage
from zope.app.file.interfaces import IFileStorage
from zope.app.file.interfaces import IReadMime, IWriteMime, IMime
from zope.app.file.interfaces import IFile, IFileContent

# TODO: remove it, just for testing
from zope.proxy import isProxy


# set the size of the chunks
MAXCHUNKSIZE = 1 << 16


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


class FileStorage(Persistent):
    """A persistent storage storing binary file data
    Let's test the constructor:

    >>> storage = FileStorage()
    >>> str(storage._data)
    ''

    >>> storage = FileStorage('Foobar')
    >>> str(storage._data)
    'Foobar'

    >>> storage = FileStorage(None)
    Traceback (most recent call last):
    ...
    TypeError: Cannot set None data on a file.

    Let's test read method:

    >>> storage = FileStorage('Foobar')
    >>> storage.read()
    'Foobar'

    Let's test write method:

    >>> storage.write('Foobar'*2)
    >>> str(storage._data)
    'FoobarFoobar'

    Let's test large data input:

    >>> storage = FileStorage()

    Insert as string:

    >>> storage.write('Foobar'*60000)
    >>> storage.getSize()
    360000
    >>> str(storage._data) == 'Foobar'*60000
    True

    Insert data as FileChunk:

    >>> fc = FileChunk('Foobar'*4000)
    >>> storage.write(fc)
    >>> storage.getSize()
    24000
    >>> str(storage._data) == 'Foobar'*4000
    True

    Insert data from storage object:

    >>> import cStringIO
    >>> sio = cStringIO.StringIO()
    >>> sio.write('Foobar'*100000)
    >>> sio.seek(0)
    >>> storage.write(sio)
    >>> storage.getSize()
    600000
    >>> str(storage._data) == 'Foobar'*100000
    True


    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IFileStorage.implementedBy(FileStorage)
    True
    >>> verifyClass(IFileStorage, FileStorage)
    True
    """

    implements(IFileStorage)    

    def __init__(self, data=''):
        self._data = None
        self._size = None
        self.write(data)

    def read(self):
        if isinstance(self._data, FileChunk):
            return str(self._data)
        else:
            return self._data

    def write(self, data):
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
        return self._size

    size = getSize


class Mime(Persistent):
    """A persistent content component storing binary file data

    Let's test the constructor:

    >>> mime = Mime()
    >>> mime.data
    ''
    >>> mime.mimeType
    ''
    >>> mime.encoding == ''
    True

    >>> mime = Mime('Foobar')
    >>> mime.data
    'Foobar'
    >>> mime.mimeType
    ''
    >>> mime.encoding == ''
    True

    >>> mime = Mime('Foobar', 'text/plain')
    >>> mime.data
    'Foobar'
    >>> mime.mimeType
    'text/plain'
    >>> mime.encoding == ''
    True

    >>> mime = Mime(data='Foobar', mimeType='text/plain')
    >>> mime.data
    'Foobar'
    >>> mime.encoding == ''
    True

    >>> mime = Mime('Foobar', 'text/plain', 'UTF-8')
    >>> mime.data
    'Foobar'
    >>> mime.mimeType
    'text/plain'
    >>> mime.encoding
    'UTF-8'

    >>> mime = Mime(data='Foobar', mimeType='text/plain', encoding='UTF-8')
    >>> mime.data
    'Foobar'
    >>> mime.mimeType
    'text/plain'
    >>> mime.encoding
    'UTF-8'


    Let's test the mutators:

    >>> mime.data = 'Foobar'
    >>> mime.data
    'Foobar'

    >>> mime = Mime()
    >>> mime.mimeType = 'text/plain'
    >>> mime.mimeType
    'text/plain'

    >>> mime = Mime()
    >>> mime.encoding = 'UTF-8'
    >>> mime.encoding
    'UTF-8'

    >>> mime.data = None
    Traceback (most recent call last):
    ...
    TypeError: Cannot set None data on a file.


    Let's test large data input:

    >>> mime = Mime()

    Insert as string:

    >>> mime.data = 'Foobar'*60000
    >>> mime.getSize()
    360000
    >>> mime.open().read() == 'Foobar'*60000
    True

    Insert data as FileChunk:

    >>> fc = FileChunk('Foobar'*4000)
    >>> mime.data = fc
    >>> mime.getSize()
    24000
    >>> mime.data == 'Foobar'*4000
    True

    Insert data from file object:

    >>> import cStringIO
    >>> sio = cStringIO.StringIO()
    >>> sio.write('Foobar'*100000)
    >>> sio.seek(0)
    >>> mime.data = sio
    >>> mime.getSize()
    600000
    >>> mime.data == 'Foobar'*100000
    True


    Test open(mode='r') method:
    
    >>> mime = Mime('Foobar')
    >>> file = mime.open('r')
    >>> file.read()
    'Foobar'

    >>> file.size()
    6
    
    >>> file.write('sometext')
    Traceback (most recent call last):
    ...
    AttributeError: 'ReadFileStorage' object has no attribute 'write'

    >>> file = mime.open(mode='w')
    >>> file.write('Foobar'*2)
    >>> mime.open().read()
    'FoobarFoobar'

    >>> file.read()
    Traceback (most recent call last):
    ...
    AttributeError: 'WriteFileStorage' object has no attribute 'read'

    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IMime.implementedBy(Mime)
    True
    >>> verifyClass(IMime, Mime)
    True
    """
    
    implements(IMime)

    def __init__(self, data='', mimeType='', encoding=''):
        self._data = FileStorage(data)
        self.mimeType = mimeType
        self.encoding = encoding

    # IMime
    mimeType = FieldProperty(IMime['mimeType'])

    encoding = FieldProperty(IMime['encoding'])

    def _getData(self):
        return self._data.read()
        
    def _setData(self, data):
        self._data.write(data)

    data = property(_getData, _setData)

    # IReadMime
    def getMimeType(self):
        return self.mimeType

    # IWriteMime
    def setMimeType(self, mimeType):
        self.mimeType = mimeType

    # IReadMime
    def getEncoding(self):
        return self.encoding

    # IWriteMime
    def setEncoding(self, encoding):
        self.encoding = encoding

    # IReadMime
    def getSize(self):
        return self._data.getSize()

    # IMime
    def open(self, mode='r'):
        if mode == 'r':
            return ReadFileStorage(self._data)
        if mode == 'w':
            return WriteFileStorage(self._data)
        else:
            pass
            # TODO: raise wrong file open attribute error
    

class File(Persistent):
    """
    Let's test the constructor:

    >>> file = File()
    >>> file.open('r').read()
    ''

    >>> file = File('Foobar')
    >>> file.contentType
    ''
    >>> file.open('r').read()
    'Foobar'

    >>> file = File('Foobar', 'text/plain')
    >>> file.contentType
    'text/plain'
    >>> file.open('r').read()
    'Foobar'

    >>> file = File(data='Foobar', contentType='text/plain')
    >>> file.contentType
    'text/plain'
    >>> file.open('r').read()
    'Foobar'


    Let's test the mutators:

    >>> file = File()
    >>> file.contentType = 'text/plain'
    >>> file.contentType
    'text/plain'

    >>> file.open('w').write('Foobar')
    >>> file.open('r').read()
    'Foobar'

    >>> file.open('w').write(None)
    Traceback (most recent call last):
    ...
    TypeError: Cannot set None data on a file.


    Let's test large data input:

    >>> file = File()

    Insert as string:

    >>> file.open('w').write('Foobar'*60000)
    >>> file.getSize()
    360000
    >>> file.open('r').read() == 'Foobar'*60000
    True

    Insert data as FileChunk:

    >>> fc = FileChunk('Foobar'*4000)
    >>> file.open('w').write(fc)
    >>> file.getSize()
    24000
    >>> file.open('r').read() == 'Foobar'*4000
    True

    Insert data from file object:

    >>> import cStringIO
    >>> sio = cStringIO.StringIO()
    >>> sio.write('Foobar'*100000)
    >>> sio.seek(0)
    >>> file.open('w').write(sio)
    >>> file.getSize()
    600000
    >>> file.open('r').read() == 'Foobar'*100000
    True


    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IFile.implementedBy(File)
    True
    >>> verifyClass(IFile, File)
    True

    BBB: test backward compatibility:

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


    Let's test large data input for BBB files:

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

    """

    implements(IFile, IReadMime, IWriteMime, IFileContent)

    def __init__(self, data='', contentType=''):
        self.contents = Mime(data, contentType)

    contents = FieldProperty(IFile['contents'])

    def getMimeType(self):
        return self.contents.mimeType

    def setMimeType(self, mimeType):
        self.contents.mimeType = mimeType

    def getEncoding(self):
        return self.contents.encoding

    def setEncoding(self, encoding):
        self.contents.encoding = encoding

    def getSize(self):
        return self.contents.getSize()

    # TODO: How can we integrate security in this method
    # We must support read and wirte permission on this method
    def open(self, mode='r'):
        """return a file-like object for reading or updating the file value.
        """
        if mode == 'r':
            return self.contents.open(mode='r')
        if mode == 'w':
            return self.contents.open(mode='w')
        else:
            pass
            # TODO: raise wrong file open attribute error


    # BBB: the attribute contentType is deprecated.
    def _getContentType(self):
        warn("The contentType attribute is deprecated, use getMimeType()",
            DeprecationWarning, 2)
        return self.contents.mimeType

    def _setContentType(self, contentType):
        warn("The contentType attribute is deprecated, use setMimeType()",
            DeprecationWarning, 2)
        self.contents.mimeType = contentType
    
    # BBB: remove the code below this line if removing BBB
    # since we store the contentType attriute on the File instance
    # there is no need for a property contentType, use setMimeType
    # and getMimeType instead. We use the contentType property in the Mime
    # instance in forms directly via the Schema field of the contents
    # attribute.
    contentType = property(_getContentType, _setContentType)

    def _getData(self):
        return self.open(mode='r').read()
        

    def _setData(self, data):
        self.open(mode='w').write(data)

    data = property(_getData, _setData)



class ReadFileStorage(object):
    """Adapter for file-system style read access.

    >>> content = "This is some file\\ncontent."
    >>> filestorage = FileStorage(content)
    >>> filestorage._data = content

    Test the read method:

    >>> ReadFileStorage(filestorage).read() == content
    True

    Test the lenght:

    >>> ReadFileStorage(filestorage).size() == len(content)
    True

    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IReadFileStorage.implementedBy(ReadFileStorage)
    True
    >>> verifyClass(IReadFileStorage, ReadFileStorage)
    True
    """

    implements(IReadFileStorage)

    def __init__(self, context):
        self.__context = context

    def read(self):
        return self.__context.read()

    def size(self):
        return len(self.__context.read())

    getSize = size


class WriteFileStorage(object):
    """Adapter for file-system style write access.

    >>> content = "This is some file\\ncontent."
    >>> filestorage = FileStorage(content)

    Test the write method:

    >>> WriteFileStorage(filestorage).write(content)
    >>> str(filestorage._data) == content
    True

    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IWriteFileStorage.implementedBy(WriteFileStorage)
    True
    >>> verifyClass(IWriteFileStorage, WriteFileStorage)
    True
    """

    implements(IWriteFileStorage)

    def __init__(self, context):
        self.__context = context

    def write(self, data):
        self.__context.write(data)


# TODO, this is used in external editor, check if we can replace it.
class FileReadFile(object):
    """Adapter for file-system style read access.

    >>> file = File()
    >>> content = "This is some file\\ncontent."
    >>> file.data = content
    >>> file.contentType = "text/plain"
    >>> FileReadFile(file).read() == content
    True
    >>> FileReadFile(file).size() == len(content)
    True
    """
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
