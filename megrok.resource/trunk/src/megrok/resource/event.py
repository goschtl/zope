# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.security.proxy import removeSecurityProxy
from megrok.resource import include, IResourcesIncluder


@grok.subscribe(IResourcesIncluder, IBeforeTraverseEvent)
def handle_inclusion(view, event):
    view = removeSecurityProxy(view)
    needs = include.bind().get(view)
    if needs:
        for resource in needs:
            resource.need()
