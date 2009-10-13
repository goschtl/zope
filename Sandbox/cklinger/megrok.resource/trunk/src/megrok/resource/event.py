import grok
import hurry.resource

from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.security.proxy import removeSecurityProxy
from megrok.resource import include, bottom, includeall

@grok.subscribe(grok.View, IBeforeTraverseEvent)
def handle(view, event):
    view = removeSecurityProxy(view)
    all = includeall.bind().get(view)
    includes = include.bind().get(view)
    #import pdb; pdb.set_trace() 
    if all:
        for name in all.libs:

    for lib, name in includes:
        inn = getattr(lib, name)
        inn.need()
    bottom = bottom.bind().get(view)
    if botom:
        hurry.resource.bottom()
