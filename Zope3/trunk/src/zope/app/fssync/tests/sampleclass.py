##############################################################################
#
# Copyright) 2001, 2002 Zope Corporation and Contributors.
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
"""Test SampleClass for testing File-system synchronization services

$Id$
"""

from zope.fssync.server.interfaces import IObjectDirectory, IObjectFile
from zope.interface import implements

class C1: "C1 Doc"
class C2: "C2 Doc"


class CDefaultAdapter:
    """Default File-system representation for object
    """
    implements(IObjectFile)

    def __init__(self, object):
         self.context = object

    def extra(self):
         pass

    def typeIdentifier(self):
         return "Default"

    def factory(self):
         return "Default Factory"

    def getBody(self):
         return self.context.__doc__

    def setBody(self):
         pass

class CDirAdapter:
    """Directory Adapter
    """

    implements(IObjectDirectory)

    def __init__(self, object):
        self.context = object

    def extra(self):
        pass

    def typeIdentifier(self):
        return "Folder"

    def factory(self):
        return "Folder Factory"

    def contents(self):
        return []

class CFileAdapter:
    """File Adapter
    """

    implements(IObjectFile)

    def __init__(self, object):
        self.context = object

    def extra(self):
        pass

    def typeIdentifier(self):
        return "File"

    def factory(self):
        return "File Factory"

    def getBody(self):
        return self.context.__doc__

    def setBody(self):
        pass
