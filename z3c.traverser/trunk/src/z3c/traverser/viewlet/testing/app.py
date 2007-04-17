from zope.viewlet import interfaces
from zope.traversing.browser.absoluteurl import absoluteURL

class IMyManager(interfaces.IViewletManager):
    """Viewlet manager"""

class MyViewlet(object):

    def upate(self):
        pass

    def render(self):
        return '<div><a href="%s">My Viewlet</a></div>' % \
               absoluteURL(self, self.request)


