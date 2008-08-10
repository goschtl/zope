##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Additional adapters used during functional tests.
"""
import grokcore.component as grok
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.browser.interfaces import IAbsoluteURL

class CodeURL(grok.MultiAdapter):
    """An IAbsoluteURL adapter that provides faked URLs as long as we
    do not have own traversers etc. in `zope.introspectorui`.
    """
    grok.adapts(Interface, IBrowserRequest)
    grok.implements(IAbsoluteURL)
    
    def __init__(self, obj, request):
        self.obj = obj
        self.request = request
        
    def __call__(self):
        url = self.request.getApplicationURL()
        url += '/' + getattr(self.obj, 'dotted_name', '').replace('.', '/')
        if hasattr(self.obj, 'name'):
            url += '/' + self.obj.name            
        return url
