##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
$Id:$
"""
__docformat__ = "reStructuredText"

from BTrees.IFBTree import IFBTree
from BTrees.IFBTree import union
from BTrees.IFBTree import difference

import zope.interface
from zope.index.field import index as fieldindex
from zope.index.text import textindex
from zope.app.container import contained
from zc.catalog import index as zcindex
from z3c.indexer import interfaces


class IndexMixin(object):
    """Index mixin class for indexes implementing zope.index.interfaces.IInjection"""

    def doIndex(self, oid, value):
        """Index a value by its object id."""
        self.index_doc(oid, value)

    def doUnIndex(self, oid):
        """Unindex a value by its object id."""
        self.unindex_doc(oid)


class TextIndex(IndexMixin, textindex.TextIndex, contained.Contained):
    """Text index based on zope.index.text.textindex.TextIndex"""

    zope.interface.implements(interfaces.ITextIndex)


class FieldIndex(IndexMixin, fieldindex.FieldIndex,
    contained.Contained):
    """Field index based on zope.index.field.index.TextIndex
    
    Field index will use tuple in it's base apply method.
    """

    zope.interface.implements(interfaces.IFieldIndex)

    def applyEq(self, value):
        return self.apply((value, value))

    def applyNotEq(self, not_value):
        all = self.apply((None, None))
        r = self.apply((not_value, not_value))
        return difference(all, r)

    def applyBetween(self, min_value, max_value, exclude_min=False,
        exclude_max=False):
        return self.apply((min_value, max_value))

    def applyGe(self, min_value, exclude_min=False):
        return self.apply((min_value, None))

    def applyLe(self, max_value, exclude_max=False):
        return self.apply((None, max_value))

    def applyIn(self, values):
        results = []
        for value in values:
            res = self.apply((value, value))
            # empty results
            if not res:
                continue
            results.append(res)

        if not results:
            # no applicable terms at all
            return IFBTree()

        result = results.pop(0)
        for res in results:
            result = union(result, res)
        return result


class ValueIndex(IndexMixin, zcindex.ValueIndex, contained.Contained):
    """Value index based on zc.catalog.index.ValueIndex"""

    zope.interface.implements(interfaces.IValueIndex)

    def applyEq(self, value):
        return self.apply({'any_of': (value,)})

    def applyNotEq(self, not_value):
        values = list(self.values())
        if not_value in values:
            values.remove(not_value)
        return self.apply({'any_of': values})

    def applyBetween(self, min_value, max_value, exclude_min, exclude_max):
        return self.apply(
            {'between': (min_value, max_value, exclude_min, exclude_max)})

    def applyGe(self, min_value, exclude_min=False):
        return self.apply({'between': (min_value, None, exclude_min, False)})

    def applyLe(self, max_value, exclude_max=False):
        return self.apply({'between': (None, max_value, False, exclude_max)})

    def applyIn(self, values):
        return self.apply({'any_of': values})

    def applyExtentAny(self, extent):
        return self.apply({'any': extent})

    def applyExtentNone(self, extent):
        return self.apply({'none': extent})


class SetIndex(IndexMixin, zcindex.SetIndex, contained.Contained):
    """Set index based on zc.catalog.index.SetIndex"""

    zope.interface.implements(interfaces.ISetIndex)

    def applyAnyOf(self, values):
        return self.apply({'any_of': values})

    def applyAllOf(self, values):
        return self.apply({'all_of': values})

    def applyBetween(self, min_value, max_value, exclude_min, exclude_max):
        self.tuple = (min_value, max_value, exclude_min, exclude_max)
        return self.apply({'between': self.tuple})

    def applyGe(self, min_value, exclude_min=False):
        self.tuple = (min_value, None, exclude_min, False)
        return self.apply({'between': self.tuple})

    def applyLe(self, max_value, exclude_max=False):
        self.tuple = (None, max_value, False, exclude_max)
        return self.apply({'between': self.tuple})

    def applyExtentAny(self, extent):
        return self.apply({'any': extent})

    def applyExtentNone(self, extent):
        return self.apply({'none': extent})
