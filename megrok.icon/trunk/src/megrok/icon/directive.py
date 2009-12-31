# -*- coding: utf-8 -*-
import os
import martian
from sys import modules
from megrok.icon import ICONS_BASES, IIconRegistry

def validateIcon(directive, name, registry, path=None):
    if not IIconRegistry.implementedBy(registry):
        raise ValueError(
            "The specified registry is not a valid IIconRegistry.")


def feed_base(registry, name, path):
    base = ICONS_BASES.get(registry)
    if base is None:
        base = ICONS_BASES[registry] = []
    base.append((name, path))
    

class icon(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = validateIcon

    def factory(self, name, registry, path=None):
        if path is not None:
            if not os.path.isfile(path):
                pyfile = modules[self.frame.f_locals['__module__']].__file__
                path = os.path.join(os.path.dirname(pyfile), path)
                if not os.path.isfile(path):
                    raise ValueError, '%r is not a valid file' % path
            feed_base(registry, name, path)
                
        return (name, registry)
