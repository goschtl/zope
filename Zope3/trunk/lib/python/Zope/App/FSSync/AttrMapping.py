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
"""
$Id: AttrMapping.py,v 1.2 2002/10/11 06:28:05 jim Exp $
"""

__metaclass__ = type

class AttrMapping:
    """Convenience object implementing a mapping on selected object attributes
    """

    def __init__(self, context, attrs, schema=None):
        self.attrs = attrs
        self.context = context

    def __getitem__(self, name):
        if name in self.attrs:
            return getattr(self.context, name)
        raise KeyError, name

    def get(self, name, default):
        if name in self.attrs:
            return getattr(self.context, name, default)
        return default

    def __contains__(self, name):
        return (name in self.attrs) and hasattr(self.context, name)

    def __delitem__(self, name):
        if name in self.attrs:
            delattr(self.context, name)
            return
        raise KeyError, name

    def __setitem__(self, name, value):
        if name in self.attrs:
            setattr(self.context, name, value)
            return
        raise KeyError, name

    def __iter__(self):
        return iter(self.attrs)

__doc__ = AttrMapping.__doc__ + __doc__

