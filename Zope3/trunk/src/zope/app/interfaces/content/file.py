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
"""Basic File interfaces.

$Id: file.py,v 1.2 2002/12/25 14:12:59 jim Exp $
"""
import zope.schema

from zope.interface import Interface


class IReadFile(Interface):

    contentType = zope.schema.BytesLine(
        title = u'Content Type',
        description=u'The content type identifies the type of data.',
        default = 'text/plain',
        )


    data = zope.schema.Bytes(
        title = u'Data',
        description = u'The actual content of the object.',
        )

    def getData():
        """Return the contained data of the object."""

    def getContentType():
        """Returns the content type of the file using mime-types syntax."""

    def getSize():
        """Return the byte-size of the data of the object."""


class IWriteFile(Interface):

    def edit(data, contentType=None):
        """Sets the data and the content type for the object.

           Since some implementations will provide their content type
           through the data, it is good to leave the argument optional.
        """

    def setData(data):
        """Rewrite the 'file'."""

    def setContentType(contentType):
        """Sets the content type of the file."""


class IFile(IReadFile, IWriteFile):
    """The basic methods that are required to implement
       a file as a Zope Content object.

    """


class IFileContent(Interface):
    """Marker interface for content that can be managed as files.

    The default view for file content has effective URLs that don't end in
    /.  In particular, if the content included HTML, relative links in
    the HTML are relative to the container the content is in.
    """
