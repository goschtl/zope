# -*- coding: utf-8 -*-

import megrok.resource
import grokcore.component as grok

from zope.component import getAdapter
from zope.site.hooks import getSite
from zope.traversing.browser.absoluteurl import absoluteURL

from hurry.resource.interfaces import ILibraryUrl
from hurry.zoperesource.zopesupport import getRequest
from z3c.hashedresource.interfaces import IResourceContentsHash


@grok.implementer(ILibraryUrl)
@grok.adapter(megrok.resource.ILibrary)
def library_url(library):
    request = getRequest()
    use_hash = megrok.resource.use_hash.bind().get(library)
    base_url = absoluteURL(getSite(), request)

    if use_hash is True:
        resource = getAdapter(request, name=library.name)
        hashpath = IResourceContentsHash(resource)
        return '%s/@@/++noop++%s/%s' % (base_url, hashpath, library.name)
        
    return '%s/@@/%s' % (base_url, library.name)
