# -*- coding: utf-8 -*-

import martian
import grokcore.component as grok
from grokcore.view.meta.directoryresource import DirectoryResourceGrokker
from hurry.resource import ResourceInclusion, NeededInclusions
from megrok.resource.components import Library, ILibrary
from zope.interface import alsoProvides


def default_library_name(factory, module=None, **data):
    return factory.__name__.lower()


class LibraryGrokker(DirectoryResourceGrokker):
    martian.component(Library)
    martian.directive(grok.name, get_default=default_library_name)

    def execute(self, factory, config, name, path, layer, **kw):
        DirectoryResourceGrokker.execute(
            self, factory, config, name, path, layer, **kw)
        
        # We set the name using the grok.name or the class name
        # We do that only if the attribute is not already set.
        if getattr(factory, 'name', None) is None:
            factory.name = name

        # We provide ILibrary. It is needed since classProvides
        # is not inherited.
        alsoProvides(factory, ILibrary)
        
        return True    
