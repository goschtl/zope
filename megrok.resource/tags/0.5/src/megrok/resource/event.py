# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.security.proxy import removeSecurityProxy
from megrok.resource import include, IResourcesIncluder


@grok.subscribe(IResourcesIncluder, IBeforeTraverseEvent)
def handle_inclusion(includer, event):
    includer = removeSecurityProxy(includer)
    needs = include.bind().get(includer)
    if needs:
        for resource in needs:
            resource.need()
