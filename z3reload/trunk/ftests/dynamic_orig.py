from zope.publisher.browser import BrowserView


class SomeNumberView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.number = 1001


class AnotherNumberView(BrowserView):

    number = 2001


class ThirdNumberView(BrowserView):

    def __call__(self):
        return '3001'
