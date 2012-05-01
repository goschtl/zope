import fanstatic
import zope.app.wsgi.testlayer
import grokcore.resource

class BrowserLayer(zope.app.wsgi.testlayer.BrowserLayer):

    def setup_middleware(self, app):
        return fanstatic.Fanstatic(app)

browser_layer = BrowserLayer(grokcore.resource)
