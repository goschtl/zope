# -*- coding: utf-8 -*-

import os
import megrok.icon
from megrok.icon import getIconsRegistry, queryIconsRegistry
from zope.traversing.browser.absoluteurl import absoluteURL


def get_icon_url(registry, request, name):
    url = absoluteURL(registry, request)
    return '%s/%s' % (url, name)


def get_component_icon_url(component, request):
    icon, reg_name = megrok.icon.icon.bind().get(component)
    registry = queryIconsRegistry(reg_name)

    if registry is not None:
        if icon in registry:
            return get_icon_url(registry, request, icon)
    return None


def populate_icons_registry(name, path):
    registry = getIconsRegistry(name)

    if not os.path.isdir(path):
        path = os.path.join(os.path.dirname(__file__), path)
        if not os.path.isdir(path):
            raise NotImplementedError

    for root, dirs, files in os.walk(path):
        for name in files:
            ipath = os.path.join(root, name)
            iname = os.path.splitext(name)[0]
            registry.add(iname, ipath)
        dirs.remove('.svn')
