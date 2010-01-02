# -*- coding: utf-8 -*-

import os
import mimetypes
from grokcore import view, component as grok
from megrok.icon import log
from megrok.icon.interfaces import IIcon, IIconsRegistry, IIconsRegistryStorage
from zope.schema.fieldproperty import FieldProperty
from zope.security.checker import NamesChecker
from zope.browserresource.file import FileResourceFactory
from zope.publisher.interfaces.browser import IBrowserPage

CHECKER = NamesChecker(list(IBrowserPage))


class IconsStorage(dict):
    grok.implements(IIconsRegistryStorage)


class IconsRegistry(object):
    grok.baseclass()
    grok.implements(IIconsRegistry)

    allowed = FieldProperty(IIconsRegistry['allowed'])
    registry = FieldProperty(IIconsRegistry['registry'])
    subregistries = FieldProperty(IIconsRegistry['subregistries'])
    
    def add(self, name, path):
        if name in self:
            log.warning(
                "Skipping %s (%r): already in registry" % (name, path))
            return False

        mimetype, enc = mimetypes.guess_type(path)
        if mimetype in self.allowed:
            self.registry[name] = path
        else:
            print "skipping %s (%s) [WRONG MIMETYPE]" % (path, mimetype)

    def __contains__(self, name):
        return name in self.registry

    def get(self, name):
        return self.registry.get(name)

    def resource(self, name):
        path = self.get(name)
        if path is None:
            return None
        return FileResourceFactory(path, CHECKER, name)

    def __init__(self, name):
        self.name = name
        self.registry = IconsStorage()
        
