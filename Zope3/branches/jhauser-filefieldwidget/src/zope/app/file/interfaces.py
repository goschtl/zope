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
"""Basic File interfaces.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.schema import Bytes
from zope.schema import Mime, MimeData, MimeDataEncoding, MimeType
from zope.interface import Interface
from zope.app.i18n import ZopeMessageIDFactory as _

# BBB:
from zope.schema import BytesLine


class IReadFileStorage(Interface):
    """File read interface."""

    def read():
        """Read access on file."""

    def size():
        """Size of the file."""

    def getSize():
        """Size of the file."""


class IWriteFileStorage(Interface):
    """File write interface."""

    def write(data):
        """Write access on file."""


class IFileStorage(IReadFileStorage, IWriteFileStorage):
    """IFileStorage provides a read and write method for file-based objects.
    
    Objects implementing this interface handle the storage of the file
    data. Actually we provide a string implementation for smaller files
    and a FileChunk for larger files. Other storage for store a file
    blob to a SQL-Server are possible implementations.
    """


class IReadMime(Interface):
    """Mime read interface."""

    def getMimeType():
        """Return the mime-type of the file."""

    def getEncoding():
        """Return the encoding of a text-based file."""


class IWriteMime(Interface):
    """Mime write interface."""

    def setMimeType(mimeType):
        """Set the mime-type for the file object."""

    def setEncoding(mimeType):
        """Set the encoding for text-based file object."""


class IMime(IReadMime, IWriteMime):
    """Mime interface."""

    mimeType = MimeType(
        title = _(u'Content Type'),
        description=_(u'The mime-type identifies the type of data.'),
        default='',
        missing_value='',
        required=False,
        )

    encoding = MimeDataEncoding(
        title = _(u'Encoding Type'),
        description=_(u'The encoding of the data if it is text.'),
        default='',
        missing_value='',
        required=False,
        )

    data = MimeData (
        title=_(u'Data'),
        description=_(u'The actual content of the file.'),
        default='',
        missing_value='',
        required=False,
        )

    def open(mode='r'):
        """Return a file like object for reading or updating.
        
        Default is set to readonly, use mode='w' for write mode.
        """



class IFile(Interface):
    """File interface."""

    # TODO: rember, we remove the contentType  field from the interface

    contents = Mime(
        schema=IMime,
        title = _(u'Mime file'),
        description = _(u'The mime information and file data'),
        default=None,
        missing_value=None,
        required=False,
        )
    
    # BBB: remove deprectiated field
    data = Bytes(
        title=_(u'Data'),
        description=_(u'The actual content of the object.'),
        default='',
        missing_value='',
        required=False,
        )

    # BBB: remove contentType
    contentType = BytesLine(
        title = _(u'Content Type'),
        description=_(u'The content type identifies the type of data.'),
        default='',
        missing_value='',
        required=False,
        )

    def getSize():
        """Return the byte-size of the data of the object."""

    def open(mode='r'):
        """Return a file like object for reading or updating.
        
        Default is set to readonly, use mode='w' for write mode.
        """


class IFileContent(Interface):
    """Marker interface for content that can be managed as files.

    The default view for file content has effective URLs that don't end in
    /.  In particular, if the content included HTML, relative links in
    the HTML are relative to the container the content is in.
    """


# TODO: 
# BBB, remove this interface after removing BBB and inherit the
# zope.app.image.interfaces.IImage directly form 
# zope.app.file.interface.IFile
class IImage(IFile):
    """This interface defines an Image that can be displayed."""

    def getImageSize():
        """Return a tuple (x, y) that describes the dimensions of
        the object.
        """
