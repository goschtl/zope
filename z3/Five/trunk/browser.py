##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Provide basic browser functionality

$Id$
"""
import Acquisition
from AccessControl import ClassSecurityInfo, getSecurityManager
from zExceptions import Unauthorized
from Globals import InitializeClass

class BrowserView(Acquisition.Explicit):
    security = ClassSecurityInfo()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # XXX do not create any methods on the subclass called index_html,
    # as this makes Zope 2 traverse into that first!

    def __call__(self, *args, **kw):
        # XXX this is definitely not the way Zope 3 does it..

        # XXX and it is only needed for tests so that they can all
        # views directly. ZPublisher will either find a __call__ on a
        # view class or use __browswer_default__ from
        # ViewMixinForAttributes
        if hasattr(self, 'index'):
            attr = 'index'
        else:
            attr = self.__page_attribute__
        meth = getattr(self, attr)
        if attr == '__call__':
            raise AttributeError("__call__")
        elif attr == 'index':
            return meth(self, *args, **kw)
        # XXX for some reason, validating 'index' doesn't work
        # as expected. I suspect that its because it's a
        # ViewPageTemplateFile.
        security_manager = getSecurityManager()
        if not security_manager.validate(meth, self, attr, meth):
            raise Unauthorized
        return meth(*args, **kw)

InitializeClass(BrowserView)
