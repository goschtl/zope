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

import interfaces
from zope import interface
from zope import component
from zope.schema.fieldproperty import FieldProperty
from zope.schema.interfaces import IList, ISequence
from app import O2OStringTypeRelationship

_marker = object()

def _ident(field):
    if field is None:
        return repr(field)
    return '.'.join((field.__class__.__module__,
                     field.__class__.__name__,
                     field.__name__))


class FieldRelationManager(object):

    interface.implements(interfaces.IFieldRelationManager)
    utilName = FieldProperty(interfaces.IFieldRelationManager['utilName'])

    def __init__(self, source, target=None,
                 relType=None,  utilName=u''):
        self.fOut = source
        self.fIn = target
        if relType is None:
            self.relType = ':'.join((_ident(self.fOut), _ident(self.fIn)))
        else:
            self.relType=relType
        self.utilName = utilName

    def _instantiateRelation(self, source, relTypes, target):
        return O2OStringTypeRelationship(source, relTypes, target)

    @property
    def seqIn(self):
        return ISequence.providedBy(self.fIn)

    @property
    def seqOut(self):
        return ISequence.providedBy(self.fOut)

    @property
    def util(self):
        return component.getUtility(interfaces.IO2OStringTypeRelationships,
                                    name=self.utilName)

    def getSourceTokens(self, target, relType):
        return self.util.findSourceTokens(target, relType)

    def getTargetTokens(self, source, relType):
        return self.util.findTargetTokens(source, relType)

    def getSourceRelations(self, obj, relType):
        return self.util.findSourceRelationships(obj, relType)

    def getTargetRelations(self, obj, relType):
        return self.util.findTargetRelationships(obj, relType)

    def getSourceRelationTokens(self, obj, relType):
        return self.util.findSourceRelationshipTokens(obj, relType)

    def getTargetRelationTokens(self, obj, relType):
        return self.util.findTargetRelationshipTokens(obj, relType)

    def setTargets(self, source, targets, relType):
        util = self.util
        if targets is not None:
            if not self.seqOut:
                targets = [targets]
            newTargetTokens = util.relationIndex.tokenizeValues(targets,
                                                                'targets')
        else:
            newTargetTokens = []
        sourceToken = util.relationIndex.tokenizeValues([source],
                                                        'sources').next()
        oldTargetTokens = util.findTargetTokens(source, relType)
        newTT = set(newTargetTokens)
        oldTT = set(oldTargetTokens)
        addTT = newTT.difference(oldTT)
        delTT = oldTT.difference(newTT)
        for tt in delTT:
            rel = util.relationIndex.findRelationships(
                {'sources': sourceToken,
                 'relations': relType,
                 'targets': tt})
            util.remove(rel.next())
        for addT in list(
                    util.relationIndex.resolveValueTokens(addTT, 'targets')):
            rel = self._instantiateRelation(source, [relType], addT)
            util.add(rel)

    def setTargetRelations(self, source, relations, relType):
        util = self.util
        if not self.seqOut:
            relations = [relations]
        targets = [rel.target for rel in relations]
        if targets is not None:
            newTargetTokens = list(util.relationIndex.tokenizeValues(
                                                        targets, 'targets'))
        else:
            newTargetTokens = []
        sourceToken = util.relationIndex.tokenizeValues([source],
                                                        'sources').next()
        oldTargetTokens = util.findTargetTokens(source, relType)
        newTT = set(newTargetTokens)
        oldTT = set(oldTargetTokens)
        addTT = newTT.difference(oldTT)
        delTT = oldTT.difference(newTT)
        for tt in delTT:
            rel = util.relationIndex.findRelationships(
                                        {'sources': sourceToken,
                                         'relations': relType,
                                         'targets': tt})
            util.remove(rel.next())
        rels = [(rel.target, rel) for rel in relations]
        for token, rel in zip(newTargetTokens, relations):
            if token in addTT:
                util.add(rel)

    def setSources(self, target, sources, relType):
        util = self.util
        if sources is not None:
            if not self.seqIn:
                sources = [sources]
            newSourceTokens = util.relationIndex.tokenizeValues(sources,
                                                                'sources')
        else:
            newSourceTokens = []
        targetToken = util.relationIndex.tokenizeValues([target],
                                                        'targets').next()

        oldSourceTokens = util.findSourceTokens(target, relType)
        newST = set(newSourceTokens)
        oldST = set(oldSourceTokens)
        addST = newST.difference(oldST)
        delST = oldST.difference(newST)
        for st in delST:
            rel = util.relationIndex.findRelationships(
                {'targets': targetToken,
                 'relations': relType,
                 'sources': st})
            self.util.remove(rel.next())

        for addT in list(
            util.relationIndex.resolveValueTokens(addST, 'sources')):
            rel = self._instantiateRelation(addST, [relType], target)
            self.util.add(rel)

    def tokenizeValues(self, values, index):
        return self.util.relationIndex.tokenizeValues(values, index)

    def resolveValueTokens(self, tokens, index):
        return self.util.relationIndex.resolveValueTokens(tokens, index)


class PropertyRelationManager(object):
    interface.implements(interfaces.IPropertyRelationManager)

    def __init__(self, context, propertyName):
        self.context = context
        self._field = getattr(context.__class__, propertyName)

    def getRelations(self):
        manager = self._field._manager
        if isinstance(self._field, RelationPropertyOut):
            return manager.getSourceRelations(
                                    self.context, self._field._relType)
        else:
            return manager.getTargetRelations(
                                    self.context, self._field._relType)

    def getRelationTokens(self):
        manager = self._field._manager
        if isinstance(self._field, RelationPropertyOut):
            return manager.getSourceRelationTokens(
                                    self.context, self._field._relType)
        else:
            return manager.getTargetRelationTokens(
                                    self.context, self._field._relType)


class RelationPropertyBase(object):

    def __init__(self, manager, field, name=None, uids=False, relType=None):
        if name is None:
            name = field.__name__
        if relType is None:
            relType = manager.relType
        self._relType = relType
        self._manager = manager
        self._name = name
        self._field = field
        self._uids = uids
        self._ordered = IList.providedBy(self._field)

    def _setOrder(self, inst, value):
        inst.__dict__['_o_' + self._name] = value

    def _getOrder(self, inst):
        return inst.__dict__.get('_o_' + self._name, [])

    def _sort(self, inst, seq):
        keys = list(self._getOrder(inst))
        seq = list(seq)
        if not keys:
            return seq
        def _key(i):
            try:
                return keys.index(i)
            except ValueError:
                return None
        return sorted(seq, key=_key)


class RelationPropertyOut(RelationPropertyBase):

    def __init__(self, manager, name=None, uids=False, relType=None):
        super(RelationPropertyOut, self).__init__(manager,
                                                 manager.fOut,
                                                 name,
                                                 uids,
                                                 relType)

    def __get__(self, inst, klass):
        if inst is None:
            return self
        tokens = self._manager.getTargetTokens(inst, self._relType)
        if self._ordered:
            tokens = self._sort(inst, tokens)
        if not self._uids:
            tokens = self._manager.resolveValueTokens(tokens, 'targets')
        tokens = list(tokens)
        if self._manager.seqOut:
            return tokens
        else:
            try:
                return tokens[0]
            except IndexError:
                return None

    def __set__(self, inst, value):
        if self._field.readonly:
            raise ValueError(self._name, 'field is readonly')
        self._manager.setTargets(inst, value, self._relType)
        if self._ordered:
            inst.__dict__['_o_' + self._name] = \
                        list(self._manager.tokenizeValues(value, 'targets'))


class RelationPropertyIn(RelationPropertyBase):

    def __init__(self, manager, name=None, uids=False, relType=None):
        super(RelationPropertyIn, self).__init__(manager,
                                                 manager.fIn,
                                                 name,
                                                 uids,
                                                 relType)

    def __get__(self, inst, klass):
        if inst is None:
            return self
        tokens = self._manager.getSourceTokens(inst, self._relType)
        if self._ordered:
            tokens = self._sort(inst, tokens)
        if not self._uids:
            tokens = self._manager.resolveValueTokens(tokens, 'sources')
        tokens = list(tokens)
        if self._manager.seqIn:
            return tokens
        else:
            try:
                return tokens[0]
            except IndexError:
                return None

    def __set__(self, inst, value):
        if self._field.readonly:
            raise ValueError(self._name, 'field is readonly')
        self._manager.setSources(inst, value, self._relType)
        if self._ordered:
            inst.__dict__['_o_' + self._name] = \
                        list(self._manager.tokenizeValues(value, 'sources'))


