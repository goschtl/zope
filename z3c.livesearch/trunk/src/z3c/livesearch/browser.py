from interfaces import ILiveSearchView
from zope import interface
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds
from zope.app.zapi import getUtility

try:
    from zc import resourcelibrary
    haveResourceLibrary = True
except ImportError:
    haveResourceLibrary = False

class LiveSearchView(object):
    interface.implements(ILiveSearchView)

    def __call__(self):
        if haveResourceLibrary:
            resourcelibrary.need('z3c.javascript.scriptaculous')
        return super(LiveSearchView, self).__call__()

class LiveSearchResultsView(object):

    idxName = u'getSearchableText'
    catalogName = u''

    def catalogResults(self):
        query = self.request.get('query', None)
        if query is None:
            return {}
        query = u'%s*' % query
        catalog = getUtility(ICatalog, name=self.catalogName)
        results = catalog.apply({self.idxName:query})
        return results

    def results(self):
        uidutil = getUtility(IIntIds)
        for uid, score in self.catalogResults().items():
            obj = uidutil.getObject(uid)
            info = {}
            info['obj'] = obj
            info['name'] = obj.__name__
            info['url'] = absoluteURL(obj, self.request)
            info['score'] = "%.4f" % score
            yield info

