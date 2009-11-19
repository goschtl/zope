# -*- coding: utf-8 -*-

import hurry.resource
import grokcore.component as grok
import grokcore.view as view

from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.security.proxy import removeSecurityProxy
from megrok.resource import include, need
from hurry.resource import ResourceInclusion


@grok.subscribe(view.View, IBeforeTraverseEvent)
def handle_inclusion(view, event):
    with_bottom = False
    view = removeSecurityProxy(view)
    needs = need.bind().get(view)
    for lib in needs:
        lib.need()
