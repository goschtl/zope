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


class IFileStorage(Interface):
    """IFileStorage provides a read and write method for file-based objects.
    
    Objects implementing this interface handle the storage of the file
    data. Actually we provide a string implementation for smaller files
    and a FileChunk for larger files. Other storage for store a file
    blob to a SQL-Server are possible implementations.
    """

    def read():
        """Read the file data."""

    def write(data):
        """Write the file data."""

    def getSize():
        """Returns the size of the file data."""


class IMime(Interface):

    # TODO: remove the line below
    # contentType = BytesLine(
    contentType = MimeType(
        title = _(u'Content Type'),
        description=_(u'The content type identifies the type of data.'),
        default='',
        required=False,
        missing_value=''
        )

    # TODO: remove the line below
    #encoding = BytesLine(
    encoding = MimeDataEncoding(
        title = _(u'Encoding type'),
        description=_(u'The encoding of the data if it is text.'),
        default='',
        required=False,
        missing_value=''
        )

    # TODO: remove the line below
    #data = Bytes(
    data = MimeData (
        title=_(u'Data'),
        description=_(u'The actual content of the file.'),
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


class IFile(Interface):

    content = Mime(
        title = _(u'The file data'),
        description = _(u'The mime information and file data, which can be '
                         'read as a file.'),
        default=None,
        missing_value=None,
        required=False,
        )
    
    # deprectiated field
    data = Bytes(
        title=_(u'Data'),
        description=_(u'The actual content of the object.'),
        default='',
        missing_value='',
        required=False,
        )

    # BBB: remove contentType
    # this is explicit requiered for permission reason, old classes use the 
    # interface IFile for permission settings  
    contentType = BytesLine(
        title = _(u'Content Type'),
        description=_(u'The content type identifies the type of data.'),
        default='',
        required=False,
        missing_value=''
        )

    def getSize():
        """Return the byte-size of the data of the object."""


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
