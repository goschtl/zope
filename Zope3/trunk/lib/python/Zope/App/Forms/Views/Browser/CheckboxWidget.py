
from Zope.Publisher.Browser.BrowserView import BrowserView

class CheckboxWidget(BrowserView):
    def render(self):
        return '<input type="checkbox" name="%s" value="%s" />' %\
               (self.context.title, self.context.default)
    
