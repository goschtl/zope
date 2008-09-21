import grok

from gbepastebin.app import Application
from gbepastebin.rest import Utils
    
class AppTraverser(grok.Traverser):
    grok.context(Application)
    
    def traverse(self, name):
        if name == 'languages':
            if grok.IRESTLayer.providedBy(self.request):
                return Utils()
        paste=self.context.get_paste(name)
        if paste:
            return paste
        self.request.response.setStatus(404)
        return None

class ManagePermission(grok.Permission):
    grok.name('gbepastebin.manage')
