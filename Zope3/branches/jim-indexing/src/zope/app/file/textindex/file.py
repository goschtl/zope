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
"""File content component

$Id$
"""
from zope.app.file.interfaces import IFile
from zope.app.index.interfaces.text import ISearchableText
from zope.interface import implements

# XXX need a test here!

class SearchableText(object):
    """Make File objects searchable."""

    implements(ISearchableText)
    __used_for__ = IFile

    def __init__(self, file):
        self.file = file

    def getSearchableText(self):
        if self.file.contentType == "text/plain":
            return [unicode(self.file.data)]
        else:
            return None
