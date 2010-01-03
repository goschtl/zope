from zope.publisher.browser import BrowserView

class HelloView(BrowserView):

    def __call__(self):
          return "Hello"
