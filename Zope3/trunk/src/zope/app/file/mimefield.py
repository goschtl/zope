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

$Id: $
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from transaction import get_transaction
from zope.interface import implements

from zope.schema.interfaces import IField,IBytesLine
from zope.schema._bootstrapfields import Field
from zope.schema._bootstrapfields import TextLine, Int

from zope.publisher.browser import FileUpload
from zope.app.file.file import FileChunk
from interfaces import IFile

# set the size of the chunks
MAXCHUNKSIZE = 1 << 16

#
# The basic schema interface
#
class IMime(IField, IBytesLine):
    u"""Fields which hold data characterized by a mime type.

    The data is stored memory effecient.
    """

    mimetype = TextLine(title=_(u"Mime type"),
                        description=_(u"The mime type of the stored data")
                        required=False,
                        default=u"application/octet-stream"
                        )

    def getSize():
        u"""Return the size of the stored data in bytes."""

class IFileData(IMime):
    u"""Fields which hold uploaded data, mainly file type data"""
    
    filename = TextLine(title=_(u"Filename"),
                        description=_(u"The Filename of the uploaded file"),
                        required=False)

    
 # The field implementation                       
class FileData(BytesLine):
    """A field implementation for uploaded files. 

    Let's test the constructor:

    >>> file = FileData()
    >>> file.contentType
    ''
    >>> file.data
    ''

    >>> file = FileData('Foobar')
    >>> file.contentType
    ''
    >>> file.data
    'Foobar'

    >>> file = FileData('Foobar', 'text/plain')
    >>> file.contentType
    'text/plain'
    >>> file.data
    'Foobar'

    >>> file = FileData(data='Foobar', contentType='text/plain')
    >>> file.contentType
    'text/plain'
    >>> file.data
    'Foobar'


    Let's test the mutators:

    >>> file = FileData()
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

    >>> file = FileData()

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

    implements(IFileData, IFile)

    # reimplementing the old file class, which stores data in a chunked
    # data structure. As we inherit from BytesLine we are an 'Attribute'.
    def __init__(self, data='', contentType=''):
        self.data = data
        # do we need to support self.contentType for IFile?
        self.mimeType = contentType

    def _getData(self):
        if isinstance(self._data, FileChunk):
            return str(self._data)
        else:
            return self._data

    def _setData(self, data):
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

        # Handle case when data is a file object.
        seek = data.seek
        read = data.read

        # if it is a fileupload object
        if hasattr(data,'filename'):
            fid = data.filename
            # prepare from ospath filenames from explorer.
            fid=fid[max(fid.rfind('/'),
                        fid.rfind('\\'),
                        fid.rfind(':')
                              )+1:]
            self.filename = fid
        else:
            self.filename = ''
        
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

    # See IFile.
    data = property(_getData, _setData)
    
