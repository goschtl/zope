##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Ratings Manager

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zope.component
import zope.interface
from BTrees import OOBTree
from zope import annotation
from zope.app.container import contained

from lovely.rating import IRatable, IRatingsManager, IRatingDefinition, rating

class RatingsManager(contained.Contained, persistent.Persistent):
    zope.interface.implements(IRatingsManager)
    zope.component.adapts(IRatable)

    def __init__(self):
        self._storage = OOBTree.OOBTree()

    def _getDefinition(self, id):
        defn = zope.component.queryUtility(IRatingDefinition,
                                           context=self,
                                           name=id)
        if defn is None:
            raise ValueError('No rating definition named %r found.' % id)
        return defn

    def rate(self, id, value, user):
        """See interfaces.IRatingsManager"""
        defn = self._getDefinition(id)

        if not defn.scoreSystem.isValidScore(value):
            raise ValueError('Invalid rating value %r for %r.' %(value, id))

        if id not in self._storage:
            self._storage[id] = OOBTree.OOBTree()
            contained.contained(self._storage[id], self._storage, id)

        self._storage[id][user] = rating.Rating(id, value, user)
        contained.contained(self._storage[id][user], self._storage[id], user)

    def remove(self, id, user):
        """See interfaces.IRatingsManager"""
        # Just get the definition to make sure it exists.
        defn = self._getDefinition(id)

        if id not in self._storage or user not in self._storage[id]:
            return
        del self._storage[id][user]
        if len(self._storage[id]) == 0:
            del self._storage[id]

    def getRatings(self, id):
        """See interfaces.IRatingsManager"""
        # Just get the definition to make sure it exists.
        defn = self._getDefinition(id)

        return list(self._storage.get(id, {}).values())

    def getRating(self, id, user):
        """See interfaces.IRatingsManager"""
        # Just get the definition to make sure it exists.
        defn = self._getDefinition(id)

        if id not in self._storage or user not in self._storage[id]:
            return

        return self._storage[id][user]

    def computeAverage(self, id):
        """See interfaces.IRatingsManager"""
        # Just get the definition to make sure it exists.
        defn = self._getDefinition(id)
        ratings = self._storage.get(id, {}).values()
        total = sum([defn.scoreSystem.getNumericalValue(rating.value)
                    for rating in ratings])
        try:
            return total/len(ratings)
        except ZeroDivisionError:
            return -1

    def countScores(self, id):
        """See interfaces.IRatingsManager"""
        defn = self._getDefinition(id)

        value_count = {}
        for rating in self._storage.get(id, {}).values():
            value_count.setdefault(rating.value, 0)
            value_count[rating.value] += 1

        return [(score, value_count.get(score[0], 0))
                for score in defn.scoreSystem.scores]

    def countAmountRatings(self, id):
        """See interfaces.IRatingManager"""
        return len(self._storage.get(id, {}))
        

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.__parent__)


getRatingsManager = annotation.factory(RatingsManager)
