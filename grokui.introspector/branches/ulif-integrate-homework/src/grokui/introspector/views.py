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
"""
Views for the grok introspector.
"""

import grok
from zope import component
from zope.interface import Interface
from zope.app.folder.interfaces import IRootFolder
from zope.introspector.interfaces import IInfos

from grokui.introspector.interfaces import (IGrokRegistryIntrospector,
                                            IGrokCodeIntrospector,
                                            IGrokContentIntrospector)
from grokui.introspector.namespace import IntrospectorLayer

grok.layer(IntrospectorLayer)

class Index(grok.View):
    """The overview page.
    """
    grok.name('index.html')
    grok.context(IRootFolder)

class Registry(grok.View):
    grok.name('index')
    grok.context(IGrokRegistryIntrospector)

    def getUtilities(self):
        utils = self.context.getUtilities()
        return utils

class Code(grok.View):
    grok.name('index')
    grok.context(IGrokCodeIntrospector)

class Content(grok.View):
    grok.name('index')
    grok.context(IGrokContentIntrospector)

class Introspect(grok.View):
    grok.context(Interface)
    grok.name('index')

    def infoViews(self):
        for name, info in IInfos(self.context).infos():
            view = component.getMultiAdapter((info, self.request),
                                             name='index')
            # the introspect view is found for everything, and therefore
            # also for the IInfo adapter. This is not what we want, just
            # skip displaying a view for the IInfo if there's no more specific
            # view to be found
            if isinstance(view, Introspect):
                continue
            yield view

