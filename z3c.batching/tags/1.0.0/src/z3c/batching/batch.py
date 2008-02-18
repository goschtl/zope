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
from zope.interface.common.sequence import IFiniteSequence

from z3c.batching import interfaces


class Batch(object):
    zope.interface.implements(interfaces.IBatch)

    start = FieldProperty(interfaces.IBatch['start'])
    size = FieldProperty(interfaces.IBatch['size'])
    end = FieldProperty(interfaces.IBatch['end'])

    def __init__(self, sequence, start=0, size=20, batches=None):
        self.sequence = sequence

        length = len(sequence)
        self._length = length

        # See interfaces.IBatch
        self.start = start
        if length == 0:
            self.start = -1
        elif start >= length:
            raise IndexError('start index key out of range')

        # See interfaces.IBatch
        self.size = size
        self._trueSize = size

        if start + size >= length:
            self._trueSize = length - start

        # See interfaces.IBatch
        if length == 0:
            self.end = -1
        else:
            self.end = start + self._trueSize - 1

        if batches is None:
            batches = Batches(self)

        self.batches = batches

    @property
    def index(self):
        return self.start / self.size

    @property
    def number(self):
        """See interfaces.IBatch"""
        return self.start / self.size + 1

    @property
    def total(self):
        """See interfaces.IBatch"""
        total = self._length / self.size
        if self._length % self.size:
            total += 1
        return total

    @property
    def next(self):
        try:
            return self.batches[self.index + 1]
        except IndexError:
            return None

    @property
    def previous(self):
        idx = self.index - 1
        if idx >= 0:
            return self.batches[idx]
        return None

    @property
    def firstElement(self):
        """See interfaces.IBatch"""
        return self.sequence[self.start]

    @property
    def lastElement(self):
        """See interfaces.IBatch"""
        return self.sequence[self.end]

    def __getitem__(self, key):
        """See zope.interface.common.sequence.IMinimalSequence"""
        if key >= self._trueSize:
            raise IndexError('batch index out of range')
        return self.sequence[self.start+key]

    def __iter__(self):
        """See zope.interface.common.sequence.IMinimalSequence"""
        return iter(self.sequence[self.start: self.end+1])

    def __len__(self):
        """See zope.interface.common.sequence.IFiniteSequence"""
        return self._trueSize

    def __contains__(self, item):
        for i in self:
            if item == i:
                return True
        else:
            return False

    def __getslice__(self, i, j):
        if j > self.end:
            j = self._trueSize

        return [self[idx] for idx in range(i, j)]

    def __eq__(self, other):
        return ((self.size, self.start, self.sequence) ==
                (other.size, other.start, other.sequence))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self._trueSize != 0

    def __repr__(self):
        return '<%s start=%i, size=%i>' % (
            self.__class__.__name__, self.start, self.size)


class Batches(object):
    zope.interface.implements(IFiniteSequence)
    
    def __init__(self, batch):
        self.size = batch.size
        self.total = batch.total
        self.sequence = batch.sequence
        
        self._batches = {batch.index: batch}

    def __len__(self):
        return self.total

    def __getitem__(self, key):
        if key not in self._batches:
            if key < 0:
                key = self.total + key

            batch = Batch(
                self.sequence, key*self.size, self.size, self)
            self._batches[batch.index] = batch

        try:
            return self._batches[key]
        except KeyError:
            raise IndexError(key)

    def __getslice__(self, i, j):
        if j > self.total:
            j = self.total-1

        return [self[idx] for idx in range(i, j)]
