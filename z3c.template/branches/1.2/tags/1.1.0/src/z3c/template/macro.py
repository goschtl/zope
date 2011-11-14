##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

from StringIO import StringIO

from zope.tal.talinterpreter import TALInterpreter


class Macro(object):
    """Provides a single macro from a template for rendering."""

    def __init__(self, template, macroName, view, request, contentType):
        self.template = template
        self.macroName = macroName
        self.view = view
        self.request = request
        self.contentType = contentType

    def __call__(self, *args, **kwargs):
        program = self.template.macros[self.macroName]
        output = StringIO(u'')
        namespace = self.template.pt_getContext(self.view, self.request)
        context = self.template.pt_getEngineContext(namespace)
        TALInterpreter(program, None,
                       context, output, tal=True, showtal=False,
                       strictinsert=0, sourceAnnotations=False)()
        if not self.request.response.getHeader("Content-Type"):
            self.request.response.setHeader("Content-Type",
                                            self.contentType)
        return output.getvalue()

