# -*- coding: utf-8 -*-

from megrok.icon import IconsRegistry
from zope.browserresource.file import FileResourceFactory

_icons_registries_map = None

class IconsRegistryError(LookupError):
    def __init__(self, name):
        self.name = name
        Exception.__init__(self, str(self))

    def __str__(self):
        return "unknown icon registry: %r" % self.name


class IconsRegistriesMap(object):
    __slots__ = '_map',

    def __init__(self):
        self._map = {}

    def get(self, name):
        try:
            vtype = self._map[name]
        except KeyError:
            raise IconsRegistryError(name)
        return vtype

    def replace(self, name, factory):
        current = self._map.get(name)
        new = factory(name)
        for icon in current.registry.items():
            new.add(*icon)
        self._map[name] = new

    def register(self, name, factory):
        return self._map.setdefault(name, factory(name))

    def __contains__(self, name):
        return name in self._map


def getIconsRegistriesMap():
    if _icons_registries_map is None:
        setIconsRegistriesMap(IconsRegistriesMap())
    return _icons_registries_map


def setIconsRegistriesMap(registries_map):
    global _icons_registries_map
    _icons_registries_map = registries_map


def _clearIconsRegistriesMap():
    global _icons_registries_map
    _icons_registries_map = None


def getIconsRegistry(name):
    mapping = getIconsRegistriesMap()
    return mapping.get(name)


def queryIconsRegistry(name):
    mapping = getIconsRegistriesMap()
    try:
        return mapping.get(name)
    except IconsRegistryError:
        return None


try:
    from zope.testing.cleanup import addCleanUp
except ImportError:
    # don't have that part of Zope
    pass
else:
    addCleanUp(_clearIconsRegistriesMap)
    del addCleanUp
