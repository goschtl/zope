# -*- coding: utf-8 -*-

import os
import mimetypes
import inspect
from grokcore import view, component as grok
from megrok.icon import log, ICONS_BASES
from megrok.icon.interfaces import IIcon, IIconRegistry, IIconRegistryStorage
from zope.schema.fieldproperty import FieldProperty
from zope.security.checker import NamesChecker
from zope.browserresource.file import FileResourceFactory
from zope.publisher.interfaces.browser import IBrowserPage

CHECKER = NamesChecker(list(IBrowserPage))


class Icon(object):
    """An icon resource.
    """
    grok.implements(IIcon)
    
    def __init__(self, name, path):
        self.name = name
        self.path = path


class IconStorage(dict):
    grok.implements(IIconRegistryStorage)


class IconRegistry(grok.GlobalUtility):
    grok.baseclass()
    grok.implements(IIconRegistry)

    allowed = FieldProperty(IIconRegistry['allowed'])
    registry = FieldProperty(IIconRegistry['registry'])

    def _generate_registry(self):
        registry = IconStorage()
        return registry

    def add(self, name, path):
        if self.registered(name):
            log.warning(
                "Skipping %s (%r): already in registry" % (name, path))
            return False
        icon = Icon(name, path)
        mimetype, enc = mimetypes.guess_type(path)
        if mimetype in self.allowed:
            self.registry[name] = icon
        else:
            print "skipping %s (%s) [WRONG MIMETYPE]" % (path, mimetype)

    def consume(self, icons):
        for name, path in icons:
            self.add(name, path)

    def populate(self, path):
        if not os.path.isdir(path):
            path = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), path)
            if not os.path.isdir(path):
                raise NotImplementedError

        for root, dirs, files in os.walk(path):
            for name in files:
                ipath = os.path.join(root, name)
                iname = os.path.splitext(name)[0]
                self.add(iname, ipath)
            if '.svn' in dirs:
                dirs.remove('.svn')

    def registered(self, name):
        return name in self.registry

    def get(self, name):
        return self.registry.get(name)

    def resource(self, name):
        icon = self.get(name)
        if icon is None:
            return None
        return FileResourceFactory(icon.path, CHECKER, icon.name)

    def __init__(self):
        self.registry = self._generate_registry()
        path = view.path.bind().get(self)
        if path: self.populate(path)
        if self.__class__ in ICONS_BASES:
            self.consume(ICONS_BASES.get(self.__class__))
            del ICONS_BASES[self.__class__]
