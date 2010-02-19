# -*- coding: utf-8 -*-

import martian
from hurry.resource import ResourceInclusion
from hurry.resource.interfaces import IInclusion
from megrok.resource.components import ResourceLibrary
from megrok.resource.interfaces import IResourcesIncluder
from zope.interface import classImplements
from zope.interface.declarations import addClassAdvisor


def validateInclusion(directive, value):
    if (not IInclusion.providedBy(value) and
        not martian.util.check_subclass(value, ResourceLibrary)):
        raise ValueError(
            "You can only include IInclusion or"
            " ResourceLibrary components.")


class use_hash(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    default = True

    def factory(self, value):
        return bool(value)


class include(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    validate = validateInclusion

    def factory(self, resource):
        addClassAdvisor(_resources_advice, depth=3)
        return resource


def _resources_advice(cls):
    if include.bind().get(cls):
        if not IResourcesIncluder.implementedBy(cls):
            classImplements(cls, IResourcesIncluder)
    return cls


class resource(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE

    def factory(self, relpath, depends=None, bottom=False):
        return (relpath, depends, bottom)
