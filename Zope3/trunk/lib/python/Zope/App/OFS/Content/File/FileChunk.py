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

$Id: FileChunk.py,v 1.2 2002/06/10 23:27:57 jim Exp $
"""
import Persistence

class FileChunk(Persistence.Persistent):
    # Wrapper for possibly large data

    next = None
    
    def __init__(self, data):
        self._data = data


    def __getslice__(self, i, j):
        return self._data[i:j]


    def __len__(self):
        data = str(self)
        return len(data)


    def __str__(self):
        next = self.next
        if next is None:
            return self._data

        result = [self.data]
        while next is not None:
            self = next
            r.append(self._data)
            next = self.next
        
        return ''.join(r)
