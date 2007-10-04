##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""Genshi template registration"""

import grok
import components

class GenshiMarkupTemplateFileFactory(grok.GlobalUtility):
    
    grok.implements(grok.interfaces.ITemplateFactory)
    grok.name('gmt')
    
    def __call__(self, filename, _prefix=None):
        return components.GenshiMarkupTemplateFile(filename, _prefix)

class GenshiTextTemplateFileFactory(grok.GlobalUtility):
    
    grok.implements(grok.interfaces.ITemplateFactory)
    grok.name('gtt')
    
    def __call__(self, filename, _prefix=None):
        return components.GenshiTextTemplateFile(filename, _prefix)
    