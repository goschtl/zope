##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""FTP Views for the MessageBoard and Message component

$Id$
"""
from zope.interface import implements
from interfaces import IVirtualContentsFile, IPlainText

from zope.app.filerepresentation.interfaces import IReadDirectory
from zope.app.folder.filerepresentation import \
     ReadDirectory as ReadDirectoryBase
from zope.app.filerepresentation.interfaces import IDirectoryFactory

from message import Message


class VirtualContentsFile(object):

    implements(IVirtualContentsFile)

    def __init__(self, context):
        self.context = context

    def setContentType(self, contentType):
        '''See interface IFile'''
        pass

    def getContentType(self):
        '''See interface IFile'''
        return u'text/plain'

    contentType = property(getContentType, setContentType)

    def edit(self, data, contentType=None):
        '''See interface IFile'''
        self.setData(data)

    def getData(self):
        '''See interface IFile'''
        adapter = IPlainText(self.context)
        return adapter.getText() or u''

    def setData(self, data):
        '''See interface IFile'''
        adapter = IPlainText(self.context)
        return adapter.setText(data)

    data = property(getData, setData)

    def getSize(self):
        '''See interface IFile'''
        return len(self.getData())

    size = property(getSize)


class ReadDirectory(ReadDirectoryBase):
    """An special implementation of the directory."""
    
    implements(IReadDirectory)

    def keys(self):
        keys = self.context.keys()
        return list(keys) + ['contents']

    def get(self, key, default=None):
        if key == 'contents':
            return VirtualContentsFile(self.context)
        return self.context.get(key, default)

    def __len__(self):
        l = len(self.context)
        return l+1


class MessageFactory(object):
    """A simple message factory for file system representations."""

    implements(IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        """See IDirectoryFactory interface."""
        return Message()
