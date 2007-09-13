##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""Relationship Properties

$Id$
"""

from types import ListType, TupleType

from zope import interface

from zope.annotation.interfaces import IAttributeAnnotatable

from app import O2OStringTypeRelationship
from property import RelationPropertyOut
from interfaces import IDataRelationPropertyOut, IDataRelationship


class DataRelationship(O2OStringTypeRelationship):
    interface.implements(IDataRelationship, IAttributeAnnotatable)

    @apply
    def source():
        def get(self):
            if isinstance(self._sources, (ListType, TupleType)):
                return self._sources[0]
            return self._sources
        def set(self, value):
            self._sources = value
        return property(get, set)

    @apply
    def target():
        def get(self):
            if isinstance(self._targets, (ListType, TupleType)):
                return self._targets[0]
            return self._targets
        def set(self, value):
            self._targets = value
        return property(get, set)


class DataRelationPropertyOut(RelationPropertyOut):
    interface.implements(IDataRelationPropertyOut)

    def __init__(self, manager, name=None, uids=False, relType=None):
        super(DataRelationPropertyOut, self).__init__(manager,
                                                      name,
                                                      uids,
                                                      relType)

    def new(self, target):
        return DataRelationship(None, [self._relType], target)

    def __set__(self, inst, value):
        if self._field.readonly:
            raise ValueError(self._name, 'field is readonly')
        if value is None:
            v = None
        elif not self._manager.seqOut:
            if not IDataRelationship.providedBy(value):
                raise TypeError
            v = value
            v.source = inst
        else:
            v = value
            for val in v:
                if not IDataRelationship.providedBy(val):
                    raise TypeError
            for val in v:
                val.source = inst
        self._manager.setTargetRelations(inst, v, self._relType)
        if self._ordered:
            if value is not None:
                values = list(self._manager.tokenizeValues(value, 'relations'))
            else:
                values = []
            inst.__dict__['_o_' + self._name] = values

    def __get__(self, inst, klass):
        if inst is None:
            return self
        tokens = self._manager.getSourceRelationTokens(inst, self._relType)
        if self._ordered:
            tokens = self._sort(inst, tokens)
        if not self._uids:
            tokens = self._manager.resolveValueTokens(tokens, 'sources')
        tokens = list(tokens)
        if self._manager.seqOut:
            return tokens
        else:
            try:
                return tokens[0]
            except IndexError:
                return None

