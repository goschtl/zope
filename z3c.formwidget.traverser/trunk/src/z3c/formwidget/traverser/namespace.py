from zope.traversing.namespace import SimpleHandler
from zope.security.proxy import removeSecurityProxy

class WidgetHandler(SimpleHandler):

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        name = name.split('.')[-1]
        removeSecurityProxy(self.context).update()
        form = removeSecurityProxy(self.context)
        return form.widgets.get(name)                        