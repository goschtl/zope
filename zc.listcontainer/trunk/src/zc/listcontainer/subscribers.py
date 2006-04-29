from zope import component
import zope.lifecycleevent.interfaces

from zc.listcontainer import interfaces

@component.adapter(interfaces.IContained,
                   zope.lifecycleevent.interfaces.IObjectCopiedEvent)
def cleanCopy(new, ev):
    new.super = new.next = new.previous = None

