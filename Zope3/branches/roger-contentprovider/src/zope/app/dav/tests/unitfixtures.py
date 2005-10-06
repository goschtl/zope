##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Reusable test fictures for WebDAV tests

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from zope.interface import implements

from zope.app.filerepresentation.interfaces import IWriteFile
from zope.app.filerepresentation.interfaces import IReadDirectory
from zope.app.container.interfaces import IReadContainer
from zope.app.annotation.interfaces import IAnnotatable
from zope.app.file.interfaces import IFile

import zope.app.location

class Folder(zope.app.location.Location, Persistent):

    implements(IReadContainer, IReadDirectory)

    def __init__(self, name, level=0, parent=None):
        self.name = self.__name__ = name
        self.level=level
        self.__parent__ = parent

    def items(self):
        if self.level == 2:
            return (('last', File('last', 'text/plain', 'blablabla', self)),)
        result = []
        for i in range(1, 3):
            result.append((str(i),
                           File(str(i), 'text/plain', 'blablabla', self)))
        result.append(('sub1',
                       Folder('sub1', level=self.level+1, parent=self)))
        return tuple(result)

class File(zope.app.location.Location, Persistent):

    implements(IWriteFile, IFile)

    def __init__(self, name, content_type, data, parent=None):
        self.name = self.__name__ = name
        self.content_type = content_type
        self.data = data
        self.__parent__ = parent
        self.contentType = content_type

    def write(self, data):
        self.data = data

class FooZPT(zope.app.location.Location, Persistent):

    implements(IAnnotatable)

    def getSource(self):
        return 'bla bla bla'


