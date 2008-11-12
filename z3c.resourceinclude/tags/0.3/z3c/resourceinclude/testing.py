from zope import interface
from zope import component

from zope.app.component import hooks
from zope.app.publisher.browser.resource import Resource
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.publisher.interfaces.browser import IBrowserRequest

def setSite():
    hooks.setHooks()
    hooks.setSite(MockSite())
   
class MockSite(object):
    def getSiteManager(self):
        return component.getSiteManager()
    
class MockSiteURL(object):
    interface.implements(IAbsoluteURL)
    component.adapts(MockSite, IBrowserRequest)

    def __init__(self, site, request):
        pass

    def __str__(self):
        return 'http://nohost/site'

class MockResourceContext(object):
    def __init__(self, content_type):
        self.content_type = content_type

class MockResource(Resource):
    __name__ = 'mock'
    
    def __init__(self, request, content_type):
        self.context = MockResourceContext(content_type)
        self.request = request
        
    def browserDefault(self, request):
        return self, ()
    
    def __repr__(self):
        return u'<MockResource type="%s">' % self.context.content_type

class MockResourceFactory(object):
    def __init__(self, content_type):
        self.content_type = content_type

    def __call__(self, request):
        return MockResource(request, self.content_type)
