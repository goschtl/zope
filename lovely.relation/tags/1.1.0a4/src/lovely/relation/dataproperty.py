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

from zope.proxy import removeAllProxies
from zope.annotation.interfaces import IAttributeAnnotatable

from app import O2OStringTypeRelationship
from property import RelationPropertyOut
from interfaces import IDataRelationPropertyOut, IDataRelationship


class DataRelationship(O2OStringTypeRelationship):
    interface.implements(IDataRelationship, IAttributeAnnotatable)

    def __init__(self, target=None, field=None):
        if field is None:
            rels = []
        else:
            rels = [field._relType]
        super(DataRelationship, self).__init__(None, rels, target)

    source = O2OStringTypeRelationship.sources
    target = O2OStringTypeRelationship.targets

    def __repr__(self):
        return '<%s %r, %r, %r>'% (
                    self.__class__.__name__,
                    self.source,
                    self.target,
                    self.relations)


class DataRelationPropertyOut(RelationPropertyOut):
    interface.implements(IDataRelationPropertyOut)

    def new(self, target):
        return DataRelationship(target, self)

    def __set__(self, inst, value):
        if self._field.readonly:
            raise ValueError(self._name, 'field is readonly')
        value = removeAllProxies(value)
        if value is None:
            v = None
        elif not self._manager.seqOut:
            if not IDataRelationship.providedBy(value):
                raise TypeError
            if value.target is None:
                raise ValueError('target for data relation must not be None')
            v = value
            v.source = inst
            if v.relations == []:
                v.relations = [self._relType]
        else:
            v = [removeAllProxies(v) for v in value]
            for val in v:
                if not IDataRelationship.providedBy(val):
                    raise TypeError('%s'% val)
                if val.target is None:
                    raise ValueError('target for data relation must not be None')
            for val in v:
                val.source = inst
                if val.relations == []:
                    val.relations = [self._relType]
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

