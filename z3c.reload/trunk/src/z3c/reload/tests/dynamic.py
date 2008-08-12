import zope.interface
from zope.publisher.browser import BrowserView
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class SomeNumberView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.number = 1001


class AnotherNumberView(BrowserView):

    number = 2001


class ThirdNumberView(BrowserView):

    def __call__(self):
        return '3001'


class NumbersViewletManager(object):

    number = '2001'

    def render(self):
        res = u'VM: %s\n' %self.number
        return res + u'\n'.join([viewlet.render() for viewlet in self.viewlets])

class NumberViewlet(object):

    number = '2001'

    def render(self):
        return self.number


class NumberPagelet(object):
    template = ViewPageTemplateFile('pagelet.pt')

    number = '2001'
