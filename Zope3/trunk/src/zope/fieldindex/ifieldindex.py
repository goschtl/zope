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

"""Index Interface."""

from zope.interface import Interface

class IFieldIndex(Interface):
    """Interface for an FieldIndex."""

    def documentCount():
        """Return the number of documents in the index."""

    def search(value):
        """Execute a search on a single value. value can be either
           a basic datatype or a class instance.

           Return an IISet of docids
        """

    def index_doc(docid, value):
        "XXX"

    def unindex_doc(docid):
        "XXX"

    def has_doc(docid):
        """Returns true if docid is an id of a document in the index"""
