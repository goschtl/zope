# -*- coding: utf-8 -*-

import martian
import grokcore.component as grok
from zope.interface import directlyProvides
from megrok.resource import Library, ILibrary


def default_library_name(factory, module=None, **data):
    return factory.__name__.lower()


class LibraryGrokker(martian.ClassGrokker):
    martian.component(Library)
    martian.directive(grok.name, get_default = default_library_name)

    def execute(self, klass, config, name, **kw):
        # We set the name using the grok.name or the class name
        # We do that only if the attribute is not already set.
        if getattr(klass, 'name', None) is None:
            klass.name = name

        # We provide ILibrary. It is needed since classProvides
        # is not inherited.
        directlyProvides(klass, ILibrary)
        
        return True    
