##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: simpleviewclass.py,v 1.3 2003/01/31 10:46:18 alga Exp $
"""

import sys
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.security.checker import defineChecker, NamesChecker
from zope.proxy.context import ContextAware

class simple(ContextAware, BrowserView):

    __implements__ = IBrowserPublisher, BrowserView.__implements__

    def browserDefault(self, request):
        return self, ()

    def publishTraverse(self, request, name):
        if name == 'index.html':
            return self.index

        raise NotFound(self, name, request)

    # XXX: we need some unittests for this !!!
    def __getitem__(self, name):
        return self.index.macros[name]

    def __call__(self, *args, **kw):
        return self.index(self.request, *args, **kw)

def SimpleViewClass(src, offering=None, used_for=None, bases=()):
    if offering is None:
        offering = sys._getframe(1).f_globals

    bases += (simple, )

    class_ = type("SimpleViewClass from %s" % src, bases,
                  {'index': ViewPageTemplateFile(src, offering)})

    if used_for is not None:
        class_.__used_for__ = used_for

    return class_
