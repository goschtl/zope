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
    for resources in grokcore.resource.directives.include.bind().get(includer):
        for resource in resources:
            resource.need()

@grokcore.component.subscribe(
    grokcore.resource.interfaces.IResourcesIncluder,
    zope.contentprovider.interfaces.IBeforeUpdateEvent)
def handle_inclusion(includer, event):
    includer = zope.security.proxy.removeSecurityProxy(includer)
    for resources in grokcore.resource.directives.include.bind().get(includer):
        for resource in resources:
            resource.need()
