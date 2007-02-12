##############################################################################
#
# Copyright (c) 2003-2007 Zope Corporation and Contributors.
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
"""Batching Implementation

$Id$
"""
__docformat__ = 'restructuredtext'
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.batching import interfaces


class Batch(object):
    zope.interface.implements(interfaces.IBatch)

    start = FieldProperty(interfaces.IBatch['start'])
    size = FieldProperty(interfaces.IBatch['size'])
    end = FieldProperty(interfaces.IBatch['end'])

    def __init__(self, list, start=0, size=20):
        self._list = list
        # See interfaces.IBatch
        self.start = start
        if len(list) == 0:
            self.start = -1
        elif start >= len(list):
            raise IndexError('start index key out of range')
        # See interfaces.IBatch
        self.size = size
        self._trueSize = size
        if start + size >= len(list):
            self._trueSize = len(list) - start
        # See interfaces.IBatch
        if len(list) == 0:
            self.end = -1
        else:
            self.end = start + self._trueSize - 1

    @property
    def number(self):
        """See interfaces.IBatch"""
        return self.start / self.size + 1

    @property
    def total(self):
        """See interfaces.IBatch"""
        return len(self._list) / self.size + 1

    @property
    def next(self):
        """See interfaces.IBatch"""
        start = self.start + self.size
        if start >= len(self._list):
            return None
        return Batch(self._list, start, self.size)

    @property
    def previous(self):
        """See interfaces.IBatch"""
        start = self.start - self.size
        if start < 0:
            return None
        return Batch(self._list, start, self.size)

    @property
    def firstElement(self):
        """See interfaces.IBatch"""
        return self._list[self.start]

    @property
    def lastElement(self):
        """See interfaces.IBatch"""
        return self._list[self.end]

    def __getitem__(self, key):
        """See zope.interface.common.sequence.IMinimalSequence"""
        if key >= self._trueSize:
            raise IndexError('batch index out of range')
        return self._list[self.start+key]

    def __iter__(self):
        """See zope.interface.common.sequence.IMinimalSequence"""
        return iter(self._list[self.start:self.end+1])

    def __len__(self):
        """See zope.interface.common.sequence.IFiniteSequence"""
        return self._trueSize

    def __repr__(self):
        return '<%s start=%i, size=%i>' % (
            self.__class__.__name__, self.start, self.size)
