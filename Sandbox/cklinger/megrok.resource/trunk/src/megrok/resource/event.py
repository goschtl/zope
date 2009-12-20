# -*- coding: utf-8 -*-

import grokcore.component as grok
import grokcore.view as view

from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.security.proxy import removeSecurityProxy
from megrok.resource import include, IResourcesIncluder


@grok.subscribe(IResourcesIncluder, IBeforeTraverseEvent)
def handle_inclusion(view, event):
    with_bottom = False
    view = removeSecurityProxy(view)
    needs = include.bind().get(view)
    for resource in needs:
        resource.need()
