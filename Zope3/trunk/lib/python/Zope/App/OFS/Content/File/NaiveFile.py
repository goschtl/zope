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
$Id: NaiveFile.py,v 1.3 2002/07/19 13:12:31 srichter Exp $
"""
from Persistence import Persistent
from Zope.App.OFS.Content.File.IFile import IFile
from Zope.App.OFS.Content.File.SFile import SFile
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable


class NaiveFile(Persistent):
    """This is a very simple implementation of a file.

    WARNING: This implementation should not be used to save large amounts
             of Data.
    """
    __implements__ = IFile, SFile, IAnnotatable

    def __init__(self, data='', contentType=''):
        self.setData(data)
        self._contentType = contentType

    def __str__(self):
        return self.getData()

    def __len__(self):
        return 1
        
    def setContentType(self, contentType):
        '''See interface Zope.App.OFS.File.IFile.IFile'''
        SFile.getDescriptionFor('contentType').validate(contentType)
        self._contentType = contentType
    
    def getContentType(self):
        '''See interface Zope.App.OFS.File.IFile.IFile'''
        return self._contentType

    def edit(self, data, contentType=None):
        '''See interface Zope.App.OFS.File.IFile.IFile'''
        self._data = data
        if contentType is not None:
            self._contentType = contentType

    def getData(self):
        '''See interface Zope.App.OFS.File.IFile.IFile'''
        return self._data

    def setData(self, data):
        '''See interface Zope.App.OFS.File.IFile.IFile'''
        SFile.getDescriptionFor('data').validate(data)
        if data is not None:
            self._size = len(data)
            self._data = data

    def getSize(self):
        '''See interface Zope.App.OFS.File.IFile.IFile'''
        return self._size

    # See schema Zope.App.OFS.File.SFile.SFile
    data = property(getData, setData, None,
                    """Contains the data of the file.""")

    contentType = property(getContentType, setContentType, None,
                           """Specifies the content type of the data.""")

    size = property(getSize, None, None,
                    """Specifies the size of the file in bytes. Read only.""")
