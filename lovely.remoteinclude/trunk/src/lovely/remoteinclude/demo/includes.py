##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
__docformat__ = 'restructuredtext'

import vanilla
from zope import interface
from zope import event
from lovely.remoteinclude.interfaces import IIncludeableView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import (IContentProvider,
                                             BeforeUpdateEvent)
from time import sleep

class IIncludesLayer(IDefaultBrowserLayer):
    """Includes layer"""

class MainPage(object):
    interface.implements(IContentProvider)

    def update(self):
        sleep(1)

    def render(self):
        return self.index()

    def __call__(self):
        event.notify(BeforeUpdateEvent(self, self.request))
        self.update()
        return self.render()

class FirstViewlet(vanilla.FirstViewlet):
    interface.implements(IIncludeableView)

class SecondViewlet(vanilla.SecondViewlet):
    interface.implements(IIncludeableView)
