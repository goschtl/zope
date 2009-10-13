import grok
import hurry.resource

from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.security.proxy import removeSecurityProxy
from megrok.resource import include, bottom

@grok.subscribe(grok.View, IBeforeTraverseEvent)
def handle(view, event):
    view = removeSecurityProxy(view)
    includes = include.bind().get(view)
    for lib, name in includes:
        inn = getattr(lib, name)
        inn.need()
    bot = False    
    bot = bottom.bind().get(view)
    if bot:
        
        hurry.resource.bottom()
