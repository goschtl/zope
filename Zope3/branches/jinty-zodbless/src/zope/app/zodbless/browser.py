from zope.publisher.browser import BrowserView

class Index(BrowserView):

    def __call__(self):
        return "This Zope3 application does not use the ZODB."
