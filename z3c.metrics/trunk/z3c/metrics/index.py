import persistent
from BTrees import family64, Length

from zope import interface
import zope.event
from zope.app.event import objectevent

from z3c.metrics import interfaces, scale

class ScoreError(Exception):
    pass

class IndexesScoreEvent(objectevent.ObjectEvent):
    interface.implements(interfaces.IIndexesScoreEvent)

    def __init__(self, obj, indexes=()):
        self.object = obj
        self.indexes = indexes

class BuildScoreEvent(IndexesScoreEvent):
    interface.implements(interfaces.IBuildScoreEvent,
                         interfaces.IAddValueEvent)

class Index(persistent.Persistent):
    interface.implements(interfaces.IIndex)

    family = family64.IF

    def __init__(self, initial=0,
                 scale=scale.ExponentialDatetimeScale()):
        self.initial = initial
        self.scale = scale
        self.clear()

    def __contains__(self, obj):
        docid = self._getKeyFor(obj)
        return docid in self._scores

    def _getKeyFor(self, obj):
        raise NotImplementedError()

    def clear(self):
        self._scores = self.family.BTree()
        self._num_docs = Length.Length(0)

    def getScoreFor(self, obj, query=None):
        docid = self._getKeyFor(obj)
        raw = self._scores[docid]
        return self.scale.normalize(raw, query)

    def initScoreFor(self, obj):
        docid = self._getKeyFor(obj)
        self._num_docs.change(1)
        self._scores[docid] = self.initial

    def buildScoreFor(self, obj):
        docid = self._getKeyFor(obj)
        if docid not in self._scores:
            self._num_docs.change(1)
        self._scores[docid] = self.initial
        zope.event.notify(
            BuildScoreEvent(obj, [self]))

    def changeScoreFor(self, obj, amount):
        docid = self._getKeyFor(obj)
        old = self._scores[docid]
        self._scores[docid] = old + amount
        if self._scores[docid] == scale.inf:
            self._scores[docid] = old
            raise ScoreError('Adding %s to %s for %s is too large' % (
                amount, old, obj))

    def removeScoreFor(self, obj):
        docid = self._getKeyFor(obj)
        del self._scores[docid]
        self._num_docs.change(-1)
