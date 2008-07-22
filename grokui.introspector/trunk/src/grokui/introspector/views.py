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
from zope.interface import Interface
from zope.app.folder.interfaces import IRootFolder

from grokui.introspector.interfaces import (IGrokRegistryIntrospector,
                                            IGrokCodeIntrospector)
from grokui.introspector.namespace import IntrospectorLayer

grok.layer(IntrospectorLayer)

class Index(grok.View):
    """The overview page.
    """
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
