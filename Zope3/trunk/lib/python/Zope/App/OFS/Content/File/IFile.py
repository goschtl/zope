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

$Id: IFile.py,v 1.5 2002/09/05 18:55:02 jim Exp $
"""

from Interface import Interface
from Zope.App.OFS.Content.IFileContent import IFileContent
import Zope.Schema

class IReadFile(IFileContent):
    
    contentType = Zope.Schema.Str(
        title = 'Content Type',
        description = 'The content type identifies the type of data.',
        default = 'text/plain',
        )


    data = Zope.Schema.Str(
        title = 'Data',
        description = 'The actual content of the object.',
        )

    def getData():
        """Returns the bits (data) of the File itself."""


    def getContentType():
        """Returns the content type of the file using mime-types syntax."""


    def getSize():
        """Return the size of the file.

        Note that only the file's content is counted and not the entire
        Python object.
        """

class IWriteFile(Interface):


    def edit(data, contentType=None):
        """Sets the data and the content type for the object.

           Since some implementations will provide their content type
           through the data, it is good to leave the argument optional.
        """


    def setData(data):
        """Sets ONLY the data without changing the content type."""


    def setContentType(contentType):
        """Sets the content type of the file."""


class IFile(IReadFile, IWriteFile):
    """The basic methods that are required to implement
       a file as a Zope Content object.

    """
        
