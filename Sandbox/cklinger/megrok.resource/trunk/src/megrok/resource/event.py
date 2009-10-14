import grok
import hurry.resource

from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.security.proxy import removeSecurityProxy
from megrok.resource import include

@grok.subscribe(grok.View, IBeforeTraverseEvent)
def handle(view, event):
    with_bottom = False
    view = removeSecurityProxy(view)
    includes = include.bind().get(view)
    for lib, name, bottom in includes:
        if bottom:
            with_bottom=True
        if not name:
            for l in lib.libs:
                inn = getattr(lib, l)
                inn.need()
        else:
            inn = getattr(lib, name)
            inn.need()
    if with_bottom:
        hurry.resource.bottom()
