##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import zope.component
import zope.app.publication.interfaces
import grokcore.component
import grokcore.layout
import grokcore.layout.components
import zope.security.proxy
import zope.contentprovider.interfaces

import grokcore.resource.directives

@grokcore.component.subscribe(
    grokcore.resource.interfaces.IResourcesIncluder,
    zope.app.publication.interfaces.IBeforeTraverseEvent)
def handle_resources(includer, event):
    includer = zope.security.proxy.removeSecurityProxy(includer)
    for resources in grokcore.resource.directives.resources.bind().get(
            includer):
        for resource in resources:
            resource.need()

    # In case of a grokcore.layout.components.LayoutAware object,
    # the layout attribute is a Layout object that also can have resources.
    if not isinstance(includer, grokcore.layout.components.LayoutAware):
        return
    # Using an implementation detail of LayoutAware here.
    layout = includer._get_layout()
    if grokcore.resource.interfaces.IResourcesIncluder.providedBy(layout):
        for resources in grokcore.resource.directives.resources.bind().get(
                layout):
            for resource in resources:
                resource.need()

@grokcore.component.subscribe(
    grokcore.resource.interfaces.IResourcesIncluder,
    zope.contentprovider.interfaces.IBeforeUpdateEvent)
def handle_inclusion(includer, event):
    includer = zope.security.proxy.removeSecurityProxy(includer)
    for resources in grokcore.resource.directives.resources.bind().get(
            includer):
        for resource in resources:
            resource.need()
