# -*- coding: utf-8 -*-

import grokcore.component as grok

from megrok.icon import IIconRegistry
from megrok.icon.directive import icon
from zope.component import queryUtility
from zope.traversing.browser.absoluteurl import absoluteURL


def get_icon_url(registry, request, name):
    url = absoluteURL(registry, request)
    return '%s/%s' % (url, name)
    

def get_component_icon_url(component, request):
    name, factory = icon.bind().get(component)
    registry_name = grok.name.bind().get(factory)
    registry = queryUtility(IIconRegistry, name=registry_name)
    if registry is not None:
        if registry.registered(name):
            return get_icon_url(registry, request, name)
    return None
