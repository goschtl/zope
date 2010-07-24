# -*- coding: utf-8 -*-

from grokcore.component import baseclass
from grokcore.view import DirectoryResource
from zope.component import getUtility
from hurry.resource.interfaces import ICurrentNeededInclusions


class Library(DirectoryResource):
    """A library that exposes resources through an URL.
    This component is only used to declare a resources folder.
    """
    baseclass()
    name = None


class ResourceLibrary(Library):
    """A library that behaves like a group inclusion.
    This prevents code redundance for simple libraries with
    few resources.
    """
    baseclass()
    depends = []

    @classmethod
    def need(cls):
        needed = getUtility(ICurrentNeededInclusions)()
        needed.need(cls)

    @classmethod
    def inclusions(cls):
        """Get all inclusions needed by this inclusion.
        """
        result = []
        for depend in cls.depends:
            result.extend(depend.inclusions())
        return result
