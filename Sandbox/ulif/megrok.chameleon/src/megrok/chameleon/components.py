##############################################################################
#
# Copyright (c) 2006-2009 Zope Corporation and Contributors.
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
"""Chameleon page template components"""
import os
from chameleon.zpt.template import PageTemplateFile, PageTemplate
from grokcore.component import GlobalUtility, implements, name
from grokcore.view import interfaces
from grokcore.view.components import GrokTemplate

class ChameleonPageTemplate(GrokTemplate):
    filename = None
    
    def setFromString(self, string):
        self._filename = None
        self._template = PageTemplate(string)

    def setFromFilename(self, filename, _prefix=None):
        print "SETFROMFILE"
        self._filename = filename
        self._prefix = _prefix
        self._template = PageTemplate(
            open(os.path.join(_prefix, filename), 'rb').read())
        return

    def render(self, view):
        print "RENDER: ", view, dir(self)
        if self._filename is not None:
            self.setFromFilename(self._filename, self._prefix)
        return self._template(**self.getNamespace(view))

class ChameleonPageTemplateFactory(GlobalUtility):
    implements(grokcore.view.interfaces.ITemplateFileFactory)
    name('cpt')

    def __call__(self, filename, _prefix=None):
        print "CALL: ", filename, _prefix
        return ChameleonPageTemplate(filename=filename, _prefix=_prefix)

    
