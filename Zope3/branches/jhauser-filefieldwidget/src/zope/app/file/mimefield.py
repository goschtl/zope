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

from zope.schema.interfaces import IBytesLine
from zope.schema._bootstrapfields import Field
from zope.schema._bootstrapfields import TextLine
from zope.schema._field import BytesLine
from zope.app.file.file import File

from zope.i18nmessageid import MessageIDFactory
_ = MessageIDFactory("zope")

from interfaces import IFile

#
# The basic schema interface
#
class IMime(IBytesLine):
    u"""Fields which hold data characterized by a mime type.

    The data is stored memory effecient.
    """

    contentType = TextLine(title=_(u"Mime type"),
                        description=_(u"The mime type of the stored data"),
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
class FileData(BytesLine, File):
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
    >>> from zope.app.file.file import FileChunk
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

    Test handling of filename

    >>> file.filename == ''
    True
    
    Last, but not least, verify the interface:

    >>> from zope.interface.verify import verifyClass
    >>> IFile.implementedBy(File)
    True
    >>> verifyClass(IFile, File)
    True
    """

    implements(IFileData, IFile)

    def __init__(self, data='', contentType=''):
        self.data = data
        # instead of mimeType we use contentType as it is mandated by IFile
        self.contentType = contentType
        self.filename = self._extractFilename(data)

    def _setdata(self, data):
        File._setdata(data)
        self.filename = self._extractFilename(data)

    def _extractFilename(self, data):
        # if it is a fileupload object
        if hasattr(data,'filename'):
            fid = data.filename
            # prepare from ospath filenames from explorer.
            fid=fid[max(fid.rfind('/'),
                        fid.rfind('\\'),
                        fid.rfind(':')
                              )+1:]
            return fid
        else:
            return ''

