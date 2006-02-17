##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id: livepage.py 39651 2005-10-26 18:36:17Z oestermeier $
"""
__docformat__ = 'restructuredtext'

class Cache(object) :
    """ Simple cache that uses least recently accessed time to trim size """

    def __init__(self, size=100):
        self.data = {}
        self.size = size

    def resize(self):
        """ trim cache to no more than 95% of desired size """
        trim = max(0, int(len(self.data)-0.95*self.size))
        if trim:
            # don't want self.items() because we must sort list by access time
            values = map(None, self.data.values(), self.data.keys())
            values.sort()
            for val,k in values[0:trim]:
                try :
                    del self.data[k]
                except KeyError:
                    pass
                    
    def __delitem__(self, key) :
        try :
            del self.data[key]
        except KeyError:
            pass

    def __setitem__(self,key,val):
        if (not self.data.has_key(key) and
        len(self.data) >= self.size):
            self.resize()
        self.data[key] = (time.time(), val)

    def __getitem__(self,key):
        """ like normal __getitem__ but updates time of fetched entry """
        val = self.data[key][1]
        self.data[key] = (time.time(),val)
        return val

    def get(self,key,default=None):
        """ like normal __getitem__ but updates time of fetched entry """
        try :
            return self[key]
        except KeyError:
            return default

