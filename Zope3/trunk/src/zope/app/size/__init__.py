##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adapters that give the size of an object.

$Id$
"""
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.size.interfaces import ISized
from zope.interface import implements

class DefaultSized(object):
    implements(ISized)

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
        return _('not-available', 'n/a')

def byteDisplay(size):
    if size == 0:
        return _('0 KB')
    if size <= 1024:
        return _('1 KB')
    if size > 1048576:
        size_str = _('${size} MB')
        size_str.mapping = {'size': '%0.02f' % (size / 1048576.0)}
        return size_str
    size_str = _('${size} KB')
    size_str.mapping = {'size': '%d' % (size / 1024.0)}
    return size_str
