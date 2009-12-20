#!/usr/bin/python
# -*- coding: utf-8 -*-

from martian.util import isclass
from megrok.resource import include, IResourcesIncluder
from zope.interface import classImplements, alsoProvides

def component_includes(component, *resources):
    if isclass(component):
        if not IResourcesIncluder.implementedBy(component):
            classImplements(component, IResourcesIncluder)
    else:
        if not IResourcesIncluder.providedBy(component):
            alsoProvides(component, IResourcesIncluder)
            
    include.set(component, resources)
