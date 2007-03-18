##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Skinned Grok publication objects
"""

import zope.interface
import zope.component
from zope.app.publication.requestpublicationfactories import BrowserFactory
from zope.security.checker import selectChecker

from grok.publication import GrokBrowserPublication
from grok.components import PageTemplateFile

from interfaces import ITitle

class SkinnedBrowserPublication(GrokBrowserPublication):

    def callObject(self, request, ob):
        if getattr(ob, 'context', None) is None:
            return super(SkinnedBrowserPublication, self).callObject(request, ob)
            
        checker = selectChecker(ob)
        if checker is not None:
            checker.check(ob, '__call__')
        
        managers = dict(zope.component.getAdapters((ob.context, request, ob), 
                                                   zope.interface.Interface))
        for manager in managers.values():
            manager.update()
        
        # TODO: make template configurable (pick up from layer?)
        template = PageTemplateFile('main_template.pt')
        return template.pt_render({'managers': managers})


class SkinnedBrowserFactory(BrowserFactory):

    def __call__(self):
        request, publication = super(SkinnedBrowserFactory, self).__call__()
        return request, SkinnedBrowserPublication
