import zope.app.publication.interfaces
import grokcore.component
import zope.security.proxy
import zope.contentprovider.interfaces

import grokcore.resource.directives


@grokcore.component.subscribe(
    grokcore.resource.interfaces.IResourcesIncluder,
    zope.app.publication.interfaces.IBeforeTraverseEvent)
def handle_inclusion(includer, event):
    includer = zope.security.proxy.removeSecurityProxy(includer)
    needs = set()
    # XXX Need to fix this.
    for class_ in includer.__class__.__mro__:
        if grokcore.resource.interfaces.IResourcesIncluder.implementedBy(class_):
            father = zope.security.proxy.removeSecurityProxy(class_)
            for resources in \
                grokcore.resource.directives.include.bind().get(father):
                needs.update(resources)
    for resource in needs:
        resource.need()

@grokcore.component.subscribe(
    grokcore.resource.interfaces.IResourcesIncluder,
    zope.contentprovider.interfaces.IBeforeUpdateEvent)
def handle_inclusion(includer, event):
    includer = zope.security.proxy.removeSecurityProxy(includer)
    needs = set()
    # XXX Need to fix this.
    for class_ in includer.__class__.__mro__:
        if grokcore.resource.interfaces.IResourcesIncluder.implementedBy(class_):
            father = zope.security.proxy.removeSecurityProxy(class_)
            for resources in \
                grokcore.resource.directives.include.bind().get(father):
                needs.update(resources)
    for resource in needs:
        resource.need()
