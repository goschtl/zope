# -*- coding: utf-8 -*-

import os
import martian
from sys import modules
from megrok.icon import (
    getIconsRegistriesMap, IconsRegistry, ITemporaryIconsRegistry)
from zope.interface import directlyProvides


def icon_absolute_path(frame, path):
    if not os.path.isfile(path):
        pyfile = modules[frame.f_locals['__module__']].__file__
        path = os.path.join(os.path.dirname(pyfile), path)
        if not os.path.isfile(path):
            raise ValueError, '%r is not a valid file' % path
    return path


class icon(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE

    def factory(self, name, registry="common", path=None):
        mapping = getIconsRegistriesMap()
        if path is not None:
            if not registry in mapping:
                reg = mapping.register(registry, IconsRegistry)
                directlyProvides(reg, ITemporaryIconsRegistry)
            else:
                reg = mapping.get(registry)
                
            reg.add(name, icon_absolute_path(self.frame, path))
        else:
            reg = mapping.get(registry)
            if not name in reg:
                raise ValueError, 'Icon %r does not exist' % name

        return (name, registry)
