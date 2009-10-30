# -*- coding: utf-8 -*-

import grokcore.component as grok


from grokcore.view.components import DirectoryResource
from hurry.resource import ResourceInclusion
from hurry.resource.interfaces import ILibraryUrl
from hurry.zoperesource.zopesupport import getRequest
from megrok.resource.directive import inclusion
from zope import component
from zope.app.component.hooks import getSite
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL


def inclusions(cls):
    keys = []
    values = []
    resources = inclusion.bind().get(cls)
    for name, file, depends, bottom in resources:
        keys.append(name)
        values.append(
            ResourceInclusion(cls, file, depends=depends, bottom=bottom)
            )
    return keys, values


class Library(DirectoryResource):
    grok.baseclass()
    
    _ri_keys = None
    _resources = None

    @classmethod
    def get_resources(cls, name=None):
        """ cls._resources is a dict with the name of the inclusion as key
            and the instance of a ResourceInclusion as value
        """    
        if cls._resources == None:
            cls._ri_keys, values = inclusions(cls)
            cls._resources = dict(zip(cls._ri_keys, values))
        if name is not None:
            return [cls._resources[name],]
        return [cls._resources[name] for name in cls._ri_keys]

    @classmethod
    def get(cls, value):
        return cls.get_resources(value)[0]

@grok.adapter(Library)
@grok.implementer(ILibraryUrl)
def library_url(library):
    print "libraryurl from component"
    request = getRequest()
    return "%s/@@/%s" % (AbsoluteURL(getSite(), request), library.name)
