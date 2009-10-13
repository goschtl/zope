# -*- coding: utf-8 -*-

import grok
from zope import component
from hurry.resource import ResourceInclusion
from hurry.resource.interfaces import ILibraryUrl
from zope.app.component.hooks import getSite
from grokcore.view.components import DirectoryResource
from zope.traversing.browser.interfaces import IAbsoluteURL
from hurry.zoperesource.zopesupport import getRequest

from megrok.resource import Library
from zope.interface import Interface


@grok.adapter(Interface)
@grok.implementer(ILibraryUrl)
def library_url(library):
    request = getRequest()
    return str(component.getMultiAdapter((getSite(), request),
                                         IAbsoluteURL)) + '/@@/' + library.name
        
