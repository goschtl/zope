from Zope.Publisher.Browser.BrowserView import BrowserView

class TextWidget(BrowserView):

    def render(self):
        return '<input type="text" name="%s" value="%s" />' %\
               (self.context.title, self.context.default)

