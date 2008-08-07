import grok
from zope.app.container.interfaces import IContainer

grok.context(IContainer)

class Test(grok.View):
    def render(self):
        return "This is a test"

