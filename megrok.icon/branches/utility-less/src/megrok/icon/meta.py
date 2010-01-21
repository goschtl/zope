# -*- coding: utf-8 -*-

import os
import martian
import megrok.icon

from megrok.icon import (
    IconsRegistry, getIconsRegistriesMap, ITemporaryIconsRegistry,
    populate_icons_registry)


def _get_resource_path(module_info, path):
    resource_path = module_info.getResourcePath(path)
    if os.path.isdir(resource_path):
        static_module = module_info.getSubModuleInfo(path)
        if static_module is not None:
            if static_module.isPackage():
                raise martian.error.GrokError(
                    "The '%s' icon directory must not "
                    "be a python package." % path, module_info.getModule())
            else:
                raise martian.error.GrokError(
                    "A package can not contain both a '%s' "
                    "icon directory and a module named "
                    "'%s.py'" % (path, path), module_info.getModule())
    return resource_path


def default_name(factory, module=None, **data):
    return factory.__name__.lower()


class IconsRegistryGrokker(martian.ClassGrokker):
    martian.component(IconsRegistry)
    martian.priority(500)
    martian.directive(megrok.icon.path, default=None)
    martian.directive(megrok.icon.name, get_default=default_name)

    def grok(self, name, factory, module_info, **kw):
        factory.module_info = module_info
        return super(IconsRegistryGrokker, self).grok(
            name, factory, module_info, **kw)

    def execute(self, factory, config, name, path, **kw):

        mapping = getIconsRegistriesMap()
        if name in mapping:
            registry = mapping.get(name)
            if ITemporaryIconsRegistry.providedBy(registry):
                mapping.replace(name, factory)
            else:
                raise martian.error.GrokError(
                    'The icons registry %r already exists' % name, factory)
        else:
            mapping.register(name, factory)

        if path is not None:
            path = _get_resource_path(factory.module_info, path)
            populate_icons_registry(name, path)

        return True
