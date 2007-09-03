##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
"""Base implementations for relationship.

$Id$
"""
__docformat__ = "reStructuredText"

import random
import persistent
from persistent.list import PersistentList

from zope import interface
from zope import component

from zope.schema.fieldproperty import FieldProperty
from zope.cachedescriptors.property import CachedProperty

from zope.app.container.contained import Contained
from zope.app.container import btree
from BTrees import OIBTree
from zc.relationship import index
from zope.security.proxy import removeSecurityProxy
from lovely.relation.interfaces import (IRelationship,
                                        IRelations,
                                        IRelationTypes,
                                        IRelationType,
                                        IRelationTypeLookup,
                                        IOneToOneRelationship,
                                        IOneToOneRelationships,
                                        IOneToManyRelationship,
                                        IOneToManyRelationships,
                                        IO2OStringTypeRelationship,
                                        IO2OStringTypeRelationships,
                                        )


class RelationTypeLookup(object):
    interface.implements(IRelationTypeLookup)

    # Give subclasses the opportunity to override the
    # relation types utility used for lookups.

    @CachedProperty
    def relationtypes(self):
        # BBB: This should *really* use getUtility
        return component.queryUtility(IRelationTypes)

    def _lookup(self, relation):
        if isinstance(relation, basestring):
            if self.relationtypes is not None:
                return self.relationtypes[relation]
        return relation


class Relationship(Contained, persistent.Persistent, RelationTypeLookup):
    interface.implements(IRelationship)

    def __init__(self, sources, relations, targets):
        self._sources = removeSecurityProxy(sources)
        self._targets = removeSecurityProxy(targets)
        rels = PersistentList()
        for relation in relations:
            rels.append(self._lookup(relation))
        self._relations = removeSecurityProxy(rels)
        super(Relationship, self).__init__()

    @apply
    def sources():
        def get(self):
            return self._sources
        def set(self, value):
            value = removeSecurityProxy(value)
            self._sources = value
            if IRelations.providedBy(self.__parent__):
                self.__parent__.reindex(self)
        return property(get, set)

    @apply
    def targets():
        def get(self):
            return self._targets
        def set(self, value):
            value = removeSecurityProxy(value)
            self._targets = value
            if IRelations.providedBy(self.__parent__):
                self.__parent__.reindex(self)
        return property(get, set)

    @apply
    def relations():
        def get(self):
            return self._relations
        def set(self, value):
            self._relations = value
            if IRelations.providedBy(self.__parent__):
                self.__parent__.reindex(self)
        return property(get, set)

    def addRelation(self, relation):
        if relation not in self.relations:
            self.relations.append(relation)
            if IRelations.providedBy(self.__parent__):
                self.__parent__.reindex(self)

    def removeRelation(self, relation):
        if relation in self.relations:
            self.relations.remove(relation)
            if IRelations.providedBy(self.__parent__):
                self.__parent__.reindex(self)

    def __repr__(self):
        return '<%s %r>'%(self.__class__.__name__, self.__name__)


def intIdDump(obj, idx, cache):
    # allows to use intids or objects for the tokenizer
    # this allows to use intids instead of objects to be passed to all query
    # functions.
    if isinstance(obj, int):
        return obj
    return index.generateToken(obj, idx, cache)

intIdLoad = index.resolveToken


class Relations(btree.BTreeContainer, Contained, RelationTypeLookup):
    interface.implements(IRelations)

    def __init__(self, index=None):
        idx = index
        if idx is None:
            idx = self._createIndex()
        self.relationIndex = idx
        idx.__parent__ = self
        super(Relations, self).__init__()

    def findTargets(self, source, relation=None, maxDepth=1):
        if relation is not None:
            return self.relationIndex.findValues(
                'targets',
                self.relationIndex.tokenizeQuery({'sources': source,
                                                  'relations': self._lookup(relation),
                                                  }),
                maxDepth = maxDepth,
                )
        return self.relationIndex.findValues(
            'targets', self.relationIndex.tokenizeQuery({'sources': source}),
            maxDepth = maxDepth,
            )

    def findTargetTokens(self, source, relation=None, maxDepth=1):
        if relation is not None:
            return self.relationIndex.findValueTokens(
                'targets',
                self.relationIndex.tokenizeQuery({'sources': source,
                                                  'relations': self._lookup(relation),
                                                  }),
                maxDepth = maxDepth,
                )
        return self.relationIndex.findValueTokens(
            'targets', self.relationIndex.tokenizeQuery({'sources': source}),
            maxDepth = maxDepth,
            )

    def findSources(self, target, relation=None, maxDepth=1):
        if relation is not None:
            return self.relationIndex.findValues(
                'sources',
                self.relationIndex.tokenizeQuery({'targets': target,
                                                  'relations': self._lookup(relation),
                                                  }),
                maxDepth = maxDepth,
                )
        return self.relationIndex.findValues(
            'sources',
            self.relationIndex.tokenizeQuery({'targets': target}),
            maxDepth = maxDepth,
           )

    def findSourceTokens(self, target, relation=None, maxDepth=1):
        if relation is not None:
            return self.relationIndex.findValueTokens(
                'sources',
                self.relationIndex.tokenizeQuery({'targets': target,
                                                  'relations': self._lookup(relation),
                                                  }),
                maxDepth = maxDepth,
                )
        return self.relationIndex.findValueTokens(
            'sources', self.relationIndex.tokenizeQuery({'targets': target}),
            maxDepth = maxDepth,
            )

    def findRelationships(self, source, target, relation=None):
        if relation is not None:
            return self.relationIndex.findRelationships(
                self.relationIndex.tokenizeQuery({'targets': target,
                                                  'sources': source,
                                                  'relations': self._lookup(relation),
                                                  }),
                )
        return self.relationIndex.findRelationships(
                self.relationIndex.tokenizeQuery({'sources': source,
                                                  'targets': target,
                                                  }),
                )

    def findRelationshipTokens(self, source, target, relation=None):
        if relation is not None:
            return self.relationIndex.findRelationshipTokenSet(
                self.relationIndex.tokenizeQuery({'targets': target,
                                                  'sources': source,
                                                  'relations': self._lookup(relation),
                                                  }),
                )
        return self.relationIndex.findRelationshipTokenSet(
                self.relationIndex.tokenizeQuery({'sources': source,
                                                  'targets': target,
                                                  }),
                )

    def findRelationTokens(self, relation):
        return self.relationIndex.findRelationshipTokenSet(
            self.relationIndex.tokenizeQuery({'relations': self._lookup(relation)}),
            )

    def findTargetRelationships(self, target, relation=None):
        if relation is not None:
            return self.relationIndex.findRelationships(
                   self.relationIndex.tokenizeQuery({'targets': target,
                                                      'relations': self._lookup(relation),
                                                      }),
                    )
        return self.relationIndex.findRelationships(
                    self.relationIndex.tokenizeQuery({'targets': target}),
                    )

    def findTargetRelationshipTokens(self, target, relation=None):
        if relation is not None:
            return self.relationIndex.findRelationshipTokenSet(
                    self.relationIndex.tokenizeQuery({'targets': target,
                                                      'relations': self._lookup(relation),
                                                      }),
                    )
        return self.relationIndex.findRelationshipTokenSet(
                    self.relationIndex.tokenizeQuery({'targets': target}),
                    )

    def findSourceRelationships(self, source, relation=None):
        if relation is not None:
            return self.relationIndex.findRelationships(
                    self.relationIndex.tokenizeQuery({'sources': source,
                                                      'relations': self._lookup(relation),
                                                      }),
                    )
        return self.relationIndex.findRelationships(
                    self.relationIndex.tokenizeQuery({'sources': source}),
                    )

    def findSourceRelationshipTokens(self, source, relation=None):
        if relation is not None:
            return self.relationIndex.findRelationshipTokenSet(
                    self.relationIndex.tokenizeQuery({'sources': source,
                                                      'relations': self._lookup(relation),
                                                      }),
                    )
        return self.relationIndex.findRelationshipTokenSet(
                    self.relationIndex.tokenizeQuery({'sources': source}),
                    )

    def findRelationTargets(self, relation):
        return self.relationIndex.findValues(
          'targets', self.relationIndex.tokenizeQuery({'relations': relation}),
          )

    def findRelationTargetTokens(self, relation):
        return self.relationIndex.findValueTokens(
          'targets', self.relationIndex.tokenizeQuery({'relations': relation}),
          )

    def findRelationSources(self, relation):
        return self.relationIndex.findValues(
          'sources', self.relationIndex.tokenizeQuery({'relations': relation}),
          )

    def findRelationSourceTokens(self, relation):
        return self.relationIndex.findValueTokens(
          'sources', self.relationIndex.tokenizeQuery({'relations': relation}),
          )

    def _createIndex(self):
        sources = {'element': IRelationship['sources'],
                   'dump': intIdDump,
                   'load': intIdLoad,
                   'name': 'sources'}
        relations = {'element': IRelationship['relations'],
                     'name': 'relations',
                     'multiple': True}
        targets = {'element': IRelationship['targets'],
                   'dump': intIdDump,
                   'load': intIdLoad,
                   'name': 'targets',
                   'multiple': True}

        return index.Index(
            (sources, relations, targets),
            index.TransposingTransitiveQueriesFactory('sources', 'targets'),
            )

    def add(self, item):
        key = self._generate_id(item)
        while key in self:
            key = self._generate_id(item)
        super(Relations, self).__setitem__(key, item)
        self.relationIndex.index(item)

    def remove(self, item):
        key = item.__name__
        if self[key] is not item:
            raise ValueError("Relationship is not stored as its __name__")
        self.relationIndex.unindex(item)
        super(Relations, self).__delitem__(key)

    def _generate_id(self, relationship):
        return ''.join(random.sample(
            "abcdefghijklmnopqrtstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_1234567890",
            30)) # somewhat less than 64 ** 30 variations (64*63*...*35)

    def reindex(self, target):
        assert target.__parent__ is self
        self.relationIndex.index(target)

    @property
    def __setitem__(self):
        raise AttributeError
    __delitem__ = __setitem__

    def __repr__(self):
        return '<%s %r>'%(self.__class__.__name__, self.__name__)


class RelationTypes(btree.BTreeContainer, Contained):
    interface.implements(IRelationTypes)

    def __repr__(self):
        return '<%s %r>'%(self.__class__.__name__, self.__name__)


class RelationType(persistent.Persistent, Contained):
    interface.implements(IRelationType)

    title       = FieldProperty(IRelationType['title'])
    description = FieldProperty(IRelationType['description'])

    def __init__(self, title):
        super(RelationType, self).__init__()
        self.title = title

    @property
    def name(self):
        return self.__name__

    def __repr__(self):
        return '<%s %r>'%(self.__class__.__name__, self.title)


class OneToManyRelationships(Relations):
    interface.implements(IOneToManyRelationships)


class OneToManyRelationship(Relationship):
    interface.implements(IOneToManyRelationship)

    def __init__(self, source, relations, objs=[]):
        super(OneToManyRelationship, self).__init__(source,
                                                    relations,
                                                    PersistentList())
        if objs:
            for obj in objs:
                self.targets.append(obj)
            if IRelations.providedBy(self.__parent__):
                self.__parent__.reindex(self)

    def add(self, obj):
        if not obj in self.targets:
            self.targets.append(obj)
            if IRelations.providedBy(self.__parent__):
                self.__parent__.reindex(self)

    def remove(self, obj):
        self.targets.remove(obj)
        if IRelations.providedBy(self.__parent__):
            self.__parent__.reindex(self)


class OneToOneRelationships(Relations):
    interface.implements(IOneToOneRelationships)

    def _createIndex(self):
        sources = {'element': IRelationship['sources'],
                   'dump': intIdDump,
                   'load': intIdLoad,
                   'name': 'sources'}
        relations = {'element': IRelationship['relations'],
                     'name': 'relations',
                     'multiple': True}
        targets = {'element': IRelationship['targets'],
                   'dump': intIdDump,
                   'load': intIdLoad,
                   'name': 'targets'}

        return index.Index(
            (sources, relations, targets),
            index.TransposingTransitiveQueriesFactory('sources', 'targets'),
            )


class OneToOneRelationship(Relationship):
    interface.implements(IOneToOneRelationship)


def _dlRelations(v, i, c):
    """fake dump and load for string based relations"""
    return v

class O2OStringTypeRelationships(Relations):

    """relationships which relation types are strings"""

    interface.implements(IO2OStringTypeRelationships)

    def _createIndex(self):
        sources = {'element': IRelationship['sources'],
                   'dump': intIdDump,
                   'load': intIdLoad,
                   'name': 'sources'}
        relations = {'element': IRelationship['relations'],
                     'dump': _dlRelations,
                     'load': _dlRelations,
                     'btree': OIBTree,
                     'name': 'relations',
                     'multiple': True}
        targets = {'element': IRelationship['targets'],
                   'dump': intIdDump,
                   'load': intIdLoad,
                   'name': 'targets'}

        return index.Index(
            (sources, relations, targets),
            index.TransposingTransitiveQueriesFactory('sources', 'targets'),
            )

class O2OStringTypeRelationship(Relationship):
    interface.implements(IO2OStringTypeRelationship)

