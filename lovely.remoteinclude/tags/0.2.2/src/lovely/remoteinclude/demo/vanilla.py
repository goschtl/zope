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

from time import sleep
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.viewlet import ViewletBase
from zope.dublincore.interfaces import IZopeDublinCore

class IVanillaLayer(IDefaultBrowserLayer):
    """Vanilla layer"""

class SleeperViewlet(ViewletBase):

    def update(self):
        sleep(1)

class FirstViewlet(SleeperViewlet):

    def render(self):
        title = IZopeDublinCore(self.context).title
        return u"<p>First Viewlet content: %s</p>"% title


class SecondViewlet(SleeperViewlet):

    def render(self):
        return u"<p>Second Viewlet content</p>"

