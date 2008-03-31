from zope import component

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent, Attributes
from zope.app.container.contained import dispatchToSublocations

from interfaces import IDispatcher
from interfaces import IIndexable

def objectAdded(ev):
    obj = ev.object
    if not IIndexable.providedBy(obj):
        return
    
    indexer = component.getUtility(IDispatcher)
    indexer.index(obj)

def objectModified(ev):
    obj = ev.object
    if not IIndexable.providedBy(obj):
        return

    indexer = component.getUtility(IDispatcher)
    
    if ev.descriptions:     # not used by archetypes/plone atm...
        # build the list of to be updated attributes
        attrs = []
        for desc in ev.descriptions:
            if isinstance(desc, Attributes):
                attrs.extend(desc.attributes)
        indexer.reindex(obj, attrs)
        if 'allow' in attrs:    # dispatch to sublocations on security changes
            dispatchToSublocations(obj, ev)
    else:
        # with no descriptions (of changed attributes) just reindex all
        indexer.reindex(obj)

def objectCopied(ev):
    objectAdded(ev)

def objectRemoved(ev):
    obj = ev.object
    if not IIndexable.providedBy(obj):
        return

    indexer = component.getUtility(IDispatcher)
    indexer.unindex(obj)

def objectMoved(ev):
    obj = ev.object
    if not IIndexable.providedBy(obj):
        return

    if ev.newParent is None or ev.oldParent is None:
        # it's an IObjectRemovedEvent or IObjectAddedEvent
        return

    if ev.newParent is ev.oldParent:
        # it's a renaming operation
        dispatchToSublocations(obj, ev)
    
    indexer = component.getUtility(IDispatcher)
    indexer.reindex(obj)
