# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope.interface import Interface
from hurry.zoperesource.zopesupport import getRequest
from grokcore.view.components import DirectoryResource
from megrok.resource import not_hashed
from zope.component import getAdapter, getMultiAdapter
from z3c.hashedresource.interfaces import IResourceContentsHash
from zope.app.component.hooks import getSite
from zope.traversing.browser.interfaces import IAbsoluteURL
from hurry.resource.interfaces import ILibraryUrl
from zope.interface import directlyProvides


class Library(DirectoryResource):
    grok.baseclass()

    class __metaclass__(type):
        """We do that do avoid having a grokker simply to set an attribute.
        We could also rely on the classproperty package, but this is quite
        straightforward.
        """
        def bind_grok_name(cls):
            name = grok.name.bind().get(cls)
            return name or cls.__name__.lower()
        name = property(bind_grok_name) 


@grok.adapter(Interface)
@grok.implementer(ILibraryUrl)
def library_url(library):
    request = getRequest()
    nothashed = not_hashed.bind().get(library)
    resource = getAdapter(request, name=library.name)
    hash = IResourceContentsHash(resource)
    base_url = getMultiAdapter((getSite(), request), IAbsoluteURL)
    url = '%s/@@/++noop++%s/%s' % (base_url, hash, library.name)

    if nothashed:
       url = str(getMultiAdapter((getSite(), request),
                                         IAbsoluteURL)) + '/@@/' + library.name
    return url
