from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import absoluteURL
from lovely.viewcache.interfaces import IViewCache
from zope.publisher.browser import BrowserView

class StatisticsView(BrowserView):
    """
    """
    __used_for__ = IViewCache
    
    separator='---'
    
    def invalidateItems(self):
        if 'form.Invalidate' in self.request:
            ids = self.request.get('ids', [])
            context = removeSecurityProxy(self.context)
            data = context._getStorage()._data
            for obj in data.keys():  #XXX discuss to get an method like this into viewcache interface
                for key in data[obj].keys():
                    if self.getHash(obj, None) in ids: 
                        #for invalidation of all entries for an object 
                        self.context.invalidate(obj)
                    elif self.getHash(obj, key) in ids:
                        self.context.invalidate(obj, {key[0][0]:key[0][1]})
        self.request.response.redirect(absoluteURL(self.context, self.request) + '/statistics.html')
    
    def invalidateAll(self):
        self.context.invalidateAll()
        self.request.response.redirect(absoluteURL(self.context, self.request) + '/statistics.html')
   
    def getHash(self, obj, key):
        return "%s:%s" % (hash(obj), hash(key))