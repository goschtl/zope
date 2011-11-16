##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
""" ZMI skin
"""

import zope.interface
import zope.publisher.interfaces.browser
import zope.traversing.namespace


class IZMISkin(zope.publisher.interfaces.browser.IDefaultBrowserLayer):
    """The Zope management interface exposes administrative and development
    functionality in a Zope server.
    """


class Helper(object):

    @property
    def static(self):
        return zope.traversing.namespace.getResource(
            self.context, 'zmi', self.request)
