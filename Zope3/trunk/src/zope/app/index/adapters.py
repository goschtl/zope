from zope.index.interfaces.index import IQuerying, ISimpleQuery


class SimpleQuery:
    "Call an IQuerying search, return only the hubids"
    __used_for__ = IQuerying

    def __init__(self, index):
        self._index = index

    def query(self, term, start=0, count=None):
        reslist, count = self._index.query(term, start, count)
        reslist = [ x[0] for x in reslist ]
        return reslist
