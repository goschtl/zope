# -*- coding: utf-8 -*-

import martian
from grokcore import component
from grokcore import view

from hurry.resource import ResourceInclusion
from hurry.resource.interfaces import IInclusion
from megrok.resource import Library, ILibrary, ResourceLibrary
from megrok.resource import resource
from zope.interface import alsoProvides


def default_library_name(factory, module=None, **data):
    return factory.__name__.lower()


class LibraryGrokker(martian.ClassGrokker):
    martian.component(Library)
    martian.priority(500)
    martian.directive(view.path)
    martian.directive(component.name, get_default=default_library_name)

    def execute(self, factory, config, name, path, **kw):
        # We set the name using the grok.name or the class name
        # We do that only if the attribute is not already set.
        if getattr(factory, 'name', None) is None:
            factory.name = name

        # We need to make sure the name is available for the Directory
        # Resource Grokker.
        if not component.name.bind().get(factory):
            component.name.set(factory, name)

        # We provide ILibrary. It is needed since classProvides
        # is not inherited.
        alsoProvides(factory, ILibrary)
        return True


class ResourceLibraryGrokker(martian.ClassGrokker):
    martian.component(ResourceLibrary)
    martian.directive(resource, default=[])

    def create_resources(self, library, resources):
        for (filename, depends, bottom) in resources:
            yield ResourceInclusion(
                library, filename, depends=depends, bottom=bottom)

    def execute(self, factory, config, resource, **kw):
        factory.depends = list(self.create_resources(factory, resource))
        alsoProvides(factory, IInclusion)
        return True
