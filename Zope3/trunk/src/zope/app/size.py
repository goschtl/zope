
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

$Id: size.py,v 1.1 2002/12/27 15:22:50 stevea Exp $
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
            self._sortingSize = 'bytes', size

    def sizeForSorting(self):
        """See ISized"""
        return self._sortingSize
        
    def sizeForDisplay(self):
        """See ISized"""
        units, size = self._sortingSize
        if units == 'bytes':
            result = u''
            if size < 1024:
                result = "1 KB"
            elif size > 1048576:
                result = "%0.02f MB" % (size / 1048576.0)
            else:
                result = "%d KB" % (size / 1024.0)
            return result
        return u'n/a'
