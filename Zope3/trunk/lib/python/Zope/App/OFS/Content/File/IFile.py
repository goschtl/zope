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

$Id: IFile.py,v 1.10 2002/12/20 09:25:39 srichter Exp $
"""
from Interface import Interface
import Zope.Schema

class IReadFile(Interface):
    
    contentType = Zope.Schema.BytesLine(
        title = u'Content Type',
        description=u'The content type identifies the type of data.',
        default = 'text/plain',
        )


    data = Zope.Schema.Bytes(
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
        
