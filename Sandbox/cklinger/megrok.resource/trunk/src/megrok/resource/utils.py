# -*- coding: utf-8 -*-

import grokcore.component as grok
from zope import component
from hurry.resource.interfaces import ILibraryUrl
from zope.app.component.hooks import getSite
from zope.traversing.browser.interfaces import IAbsoluteURL
from hurry.zoperesource.zopesupport import getRequest
from z3c.hashedresource.interfaces import IResourceContentsHash
from megrok.resource import Library, hashed
from zope.interface import Interface


#@grok.adapter(Library)
@grok.adapter(Interface)
@grok.implementer(ILibraryUrl)
def library_url(library):
    request = getRequest()
    is_hashed = hashed.bind().get(library)
    url = str(component.getMultiAdapter((getSite(), request),
                                         IAbsoluteURL)) + '/@@/' + library.name
    if is_hashed:
        resource = component.getAdapter(request, name=library.name)
        hash = IResourceContentsHash(resource)
        base_url = component.getMultiAdapter((getSite(), request), IAbsoluteURL)
        url = '%s/++noop++%s/@@/%s' % (url, hash, library.name)

    return url

#@grok.adapter(Interface)
#@grok.implementer(ILibraryUrl)
#def library_url(library):
#    request = getRequest()
#    return str(component.getMultiAdapter((getSite(), request),
#                                         IAbsoluteURL)) + '/@@/' + library.name
        
