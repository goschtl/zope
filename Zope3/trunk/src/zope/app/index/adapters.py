from zope.index.interfaces import IQuerying, ISimpleQuery
from zodb.btrees.IIBTree import IISet


class SimpleQuery:
    "Call an IQuerying search, return only the hubids"
    __used_for__ = IQuerying

    def __init__(self, index):
        self._index = index

    def query(self, term, start=0, count=None):
        reslist, count = self._index.query(term, start, count)
        # Not really optimal, this. May be a better way?
        reslist = IISet([ x[0] for x in reslist ])
        return reslist
