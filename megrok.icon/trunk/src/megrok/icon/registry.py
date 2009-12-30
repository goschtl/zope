# -*- coding: utf-8 -*-

import os
import mimetypes
from os.path import join, getsize
from grokcore import view, component as grok
from megrok.icon import IIcon, IIconRegistry, IIconRegistryStorage
from zc.dict import Dict
from zope.interface import directlyProvides
from zope.schema.fieldproperty import FieldProperty
from zope.security.checker import NamesChecker
from zope.browserresource.file import FileResourceFactory
from zope.publisher.interfaces.browser import IBrowserPage

ALLOWED = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']

CHECKER = NamesChecker(list(IBrowserPage))


class Icon(object):
    """An icon resource.
    """
    grok.implements(IIcon)
    
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.size = getsize(path)


class IconRegistry(grok.GlobalUtility):
    grok.baseclass()
    grok.implements(IIconRegistry)
    
    __registry__ = FieldProperty(IIconRegistry['__registry__'])
    allowed = ALLOWED

    def _generate_registry(self):
        registry = Dict()
        directlyProvides(registry, IIconRegistryStorage)
        return registry

    def add(self, name, path):
        if self.registered(name):
            log.warning(
                "Skipping %s (%r): already in registry" % (name, path))
            return False
        icon = Icon(name, path)
        mimetype, enc = mimetypes.guess_type(path)
        if mimetype in self.allowed:
            self.__registry__[name] = icon
        else:
            print "skipping %s (%s) [WRONG MIMETYPE]" % (path, icon.mimetype)

    def populate(self, path):
        if not os.path.isdir(path):
            path = os.path.join(os.path.dirname(__file__), path)
            if not os.path.isdir(path):
                raise NotImplementedError

        for root, dirs, files in os.walk(path):
            for name in files:
                ipath = os.path.join(root, name)
                iname = os.path.splitext(name)[0]
                self.add(iname, ipath)

    def registered(self, name):
        return name in self.__registry__

    def get(self, name):
        return self.__registry__.get(name)

    def resource(self, name):
        icon = self.get(name)
        if icon is None:
            return None
        return FileResourceFactory(icon.path, CHECKER, icon.name)

    def __init__(self):
        self.__registry__ = self._generate_registry()
        path = view.path.bind().get(self)
        if path: self.populate(path)
