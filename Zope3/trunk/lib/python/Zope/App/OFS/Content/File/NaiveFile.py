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

$Id: NaiveFile.py,v 1.2 2002/06/10 23:27:57 jim Exp $
"""

import Persistence
from IFile import IFile
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable


_RAISE_KEYERROR = []


class NaiveFile:
    """This is a very simple implementation of a file.

    WARNING: This implementation should not be used to save large amounts
             of Data.
    """

    __implements__ = (
        IFile,
        IAnnotatable)


    def __init__(self, data='', contentType=None):
        """ """

        self.setData(data)

        if contentType is None:
            self._contentType = ''
        else:
            self._contentType = contentType


    def __str__(self):
        return self.getData()


    def __len__(self):
        return 1
        

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.File.IFile

    def setContentType(self, contentType):
        '''See interface IFile'''
        self._contentType = contentType

        
    def getContentType(self):
        '''See interface IFile'''
        return self._contentType

        
    def edit(self, data, contentType=None):
        '''See interface IFile'''
        self._data = data
        if contentType is not None:
            self._contentType = contentType


    def getData(self):
        '''See interface IFile'''
        return self._data


    def setData(self, data):
        '''See interface IFile'''
        if data is not None:
            self._size = len(data)
        else:
            self._size = 0
        self._data = data


    def getSize(self):
        '''See interface IFile'''
        return self._size
        
    #
    ############################################################


