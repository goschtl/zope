# -*- coding: utf-8 -*-

import grok
from zope import component
from hurry.resource import ResourceInclusion
from hurry.resource.interfaces import ILibraryUrl
from zope.app.component.hooks import getSite
from grokcore.view.components import DirectoryResource
from zope.traversing.browser.interfaces import IAbsoluteURL
from hurry.zoperesource.zopesupport import getRequest

from megrok.resource.directive import inclusion
from zope.traversing.browser.absoluteurl import AbsoluteURL



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
        if cls._resources == None:
            cls._ri_keys, values = inclusions(cls)
            cls._resources = dict(zip(cls._ri_keys, values))
        if name is not None:
            return [cls._resources[name],]
        return [cls._resources[name] for name in cls._ri_keys]


@grok.adapter(Library)
@grok.implementer(ILibraryUrl)
def library_url(library):
    request = getRequest()
    return "%s/@@/%s" % (AbsoluteURL(getSite(), request), library.name)
