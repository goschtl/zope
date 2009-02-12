##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""File-based page templates that can be used as methods on views.

$Id$
"""
__docformat__ = 'restructuredtext'

import sys
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.interface import implements

from z3c.template.macro import Macro
from z3c.pagelet.browser import BrowserPagelet

from z3c.mvc import interfaces


class Controller(BrowserPagelet):
    """Page Template that only has access to a well defined model
    """
    implements(interfaces.IModelProvider)

    __required_kwargs__ = ()

    def getModel(self):
        raise NotImplemented("Subclasses must provide the getModel method")

    def render(self):
        # render content template
        if self.template is None:
            template = getMultiAdapter(
                (self, self.request), interfaces.IModelTemplate)
            return template(self)
        return self.template()

def requires(*attributes):
    frame = sys._getframe(1)
    locals = frame.f_locals
    locals.setdefault('__required_kwargs__', ())
    locals['__required_kwargs__'] += attributes

