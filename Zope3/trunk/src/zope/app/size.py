##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adapters that give the size of an object.

$Id: size.py,v 1.4 2003/01/17 00:02:06 efge Exp $
"""

from zope.app.interfaces.size import ISized

__metaclass__ = type

class DefaultSized:

    __implements__ = ISized
    
    def __init__(self, obj):
        try:
            size = int(obj.getSize())
        except (AttributeError, ValueError, TypeError):
            self._sortingSize = None, None
        else:
            self._sortingSize = 'byte', size

    def sizeForSorting(self):
        """See ISized"""
        return self._sortingSize
        
    def sizeForDisplay(self):
        """See ISized"""
        units, size = self._sortingSize
        if units == 'byte':
            return byteDisplay(size)
        return u'n/a' # XXX this should be localizable

def byteDisplay(size):
    # XXX this should be localizable
    if size == 0:
        return '0 KB'
    if size < 1024:
        return '1 KB'
    if size > 1048576:
        return '%0.02f MB' % (size / 1048576.0)
    return '%d KB' % (size / 1024.0)

