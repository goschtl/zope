# -*- coding: utf-8 -*-

import martian
import megrok.icon

from megrok.icon import (
    IconsRegistry, getIconsRegistriesMap, ITemporaryIconsRegistry,
    populate_icons_registry)


def default_name(factory, module=None, **data):
    return factory.__name__.lower()


class IconsRegistryGrokker(martian.ClassGrokker):
    martian.component(IconsRegistry)
    martian.priority(500)
    martian.directive(megrok.icon.path, default=None)
    martian.directive(megrok.icon.name, get_default=default_name)

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
            populate_icons_registry(name, path)

        return True
