# -*- coding: utf-8 -*-

import hurry.resource
import grokcore.component as grok
import grokcore.view as view

from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.security.proxy import removeSecurityProxy
from megrok.resource import include
from hurry.resource import ResourceInclusion


@grok.subscribe(view.View, IBeforeTraverseEvent)
def handle_inclusion(view, event):
    with_bottom = False
    view = removeSecurityProxy(view)
    includes = include.bind().get(view)
    for lib, name, bottom in includes:
        if bottom:
            with_bottom=True

        if isinstance(lib, ResourceInclusion):
            lib.need()
        else:
            resources = lib.get_resources(name=name)
            for resource in resources:
                resource.need()

    if with_bottom:
        hurry.resource.bottom()
