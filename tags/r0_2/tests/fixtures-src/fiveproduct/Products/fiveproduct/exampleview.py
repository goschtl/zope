from zope.interface import Interface, implements
from Products.Five import BrowserView

class IExampleView(Interface):
    
    def someRandomMethod():
        pass
    
class ExampleView(BrowserView):
    implements(IExampleView)

    def someRandomMethod(self):
        pass
