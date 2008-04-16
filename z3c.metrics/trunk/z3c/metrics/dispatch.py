from zope import interface, component
from zope.app.component import hooks
from zope.app.location import interfaces as location_ifaces
from zope.app.container import interfaces as container_ifaces
from zope.app.security import interfaces as security_ifaces

from z3c.metrics import interfaces

class IAncestors(interface.Interface):
    """Iterate over the ancestors of a contained object."""

@component.adapter(container_ifaces.IContained)
@interface.implementer(IAncestors)
def getAncestors(contained):
    ancestor = contained
    while ancestor is not None:
        yield ancestor
        ancestor = ancestor.__parent__

@component.adapter(container_ifaces.IContained,
                   interfaces.IChangeScoreEvent)
def dispatchToAncestors(obj, event):
    new_ancestors = []
    if event.newParent is not None:
        new_ancestors = list(IAncestors(event.newParent))

    old_ancestors = []
    if event.oldParent is not None:
        old_ancestors = list(IAncestors(event.oldParent))

    for new_idx in xrange(len(new_ancestors)):
        new_ancestor = new_ancestors[new_idx]
        if new_ancestor in old_ancestors:
            old_idx = old_ancestors.index(new_ancestor)
            new_ancestors = new_ancestors[:new_idx]
            old_ancestors = old_ancestors[:old_idx]
            break

    event.newAncestors = new_ancestors
    event.oldAncestors = old_ancestors

    for ancestor in new_ancestors + old_ancestors:
        for _ in component.subscribers(
            [obj, event, ancestor], None):
            pass # Just make sure the handlers run

@component.adapter(container_ifaces.IContainer,
                   interfaces.IBuildScoreEvent,
                   container_ifaces.IContainer)
def dispatchToDescendants(descendant, event, obj=None):
    if obj is None:
        obj = descendant
    subs = location_ifaces.ISublocations(descendant, None)
    if subs is not None:
        for sub in subs.sublocations():
            for ignored in component.subscribers(
                (sub, event, obj), None):
                pass # They do work in the adapter fetch

class CreatorLookup(object):
    interface.implements(interfaces.ICreatorLookup)
    component.adapts(interfaces.ICreated)

    def __init__(self, context):
        self.authentication = component.getUtility(
            security_ifaces.IAuthentication, context=context)

    def __call__(self, creator_id):
        return self.authentication.getPrincipal(creator_id)

@component.adapter(interfaces.ICreated,
                   interfaces.IChangeScoreEvent)
def dispatchToCreators(obj, event):
    creator_lookup = component.getAdapter(
        obj, interfaces.ICreatorLookup)
    for creator_id in interfaces.ICreated(obj).creators:
        for _ in component.subscribers(
            [obj, event, creator_lookup(creator_id)], None):
            pass # Just make sure the handlers run

class ICreatedDispatchEvent(interface.Interface):
    """Dispatched to subloacations for matching on creators."""

    event = interface.Attribute('Event')
    creators = interface.Attribute('Creators')

class CreatedDispatchEvent(object):
    interface.implements(ICreatedDispatchEvent)

    def __init__(self, creators):
        self.creators = creators

@component.adapter(security_ifaces.IPrincipal,
                   interfaces.IBuildScoreEvent)
def dispatchToSiteCreated(creator, event):
    dispatched = CreatedDispatchEvent(set([creator.id]))
    for _ in component.subscribers(
        [hooks.getSite(), event, dispatched], None):
        pass # Just make sure the handlers run

@component.adapter(interfaces.ICreated,
                   interfaces.IBuildScoreEvent,
                   ICreatedDispatchEvent)
def dispatchToCreated(obj, event, dispatched):
    creator_lookup = component.getAdapter(
        obj, interfaces.ICreatorLookup)
    for creator_id in dispatched.creators.intersection(
        interfaces.ICreated(obj).creators):
        for _ in component.subscribers(
            [obj, event, creator_lookup(creator_id)], None):
            pass # Just make sure the handlers run
