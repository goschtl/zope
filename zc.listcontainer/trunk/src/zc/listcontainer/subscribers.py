from zope import component
import zope.app.event.interfaces

from zc.listcontainer import interfaces

@component.adapter(interfaces.IContained,
                   zope.app.event.interfaces.IObjectCopiedEvent)
def cleanCopy(new, ev):
    new.super = new.next = new.previous = None

