##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Interfaces for multi-field index

$Id$
"""
from zope.app.catalog.interfaces import ICatalogIndex
from zope.interface import Interface


class IMultiFieldIndex(ICatalogIndex):
    """An index for multiple fields"""
    
    def apply(query):
        """See IIndexSearch for the purpose of this method.
        
        query is the dictionary which keys are names of sub-indexes
        and values are queries for those indexes.
        """

    def recreateIndexes():
        """Clear and recreate sub-indexes.
        
        Note that after using this method, newly created sub-indexes won't
        reindex current content. This may change in future.
        """


class ISubIndexFactory(Interface):
    """A factory of sub-index for multi-field index"""

    def __call__():
        """Return an index instance to be added to multi-field index"""
