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
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Field index"""

import zodb

from persistence import Persistent

from zodb.btrees.IOBTree import IOBTree
from zodb.btrees.OOBTree import OOBTree
from zodb.btrees.IIBTree import IITreeSet, IISet

from zope.fieldindex.ifieldindex import IFieldIndex

class FieldIndex(Persistent):

    __implements__ = IFieldIndex

    def __init__(self):
        self.clear()


    def clear(self):
        """ initialize forward and reverse mappings """

        # The forward index maps indexed values to a sequence
        # of docids
        self._fwd_index = OOBTree()

        # The reverse index maps a docid to its index value
        self._rev_index = IOBTree()


    def documentCount(self):
        """Return the number of documents in the index."""
        return len(self._rev_index)


    def has_doc(self, docid):
        return bool(self._rev_index.has_key(docid))


    def index_doc(self, docid, value):

        if not self._fwd_index.has_key(value):
            self._fwd_index[value] = IITreeSet()

        self._fwd_index[value].insert(docid)
        self._rev_index[docid] = value


    def unindex_doc(self, docid):

        try:      # ignore non-existing docids, don't raise
            value = self._rev_index[docid]
        except KeyError: 
            return

        del self._rev_index[docid]

        try:
            self._fwd_index[value].remove(docid)
            if len(self._fwd_index[value]) == 0:
                del self._fwd_index[value]
        except:
            pass


    def search(self, value):

        try:
            return IISet(self._fwd_index[value])
        except KeyError:
            return IISet()

