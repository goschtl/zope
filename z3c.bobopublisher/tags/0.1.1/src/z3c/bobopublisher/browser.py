##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

from zope.browser.interfaces import IBrowserView
from zope.interface import implements


class BrowserPage(object):
    """Simple browser page"""

    implements(IBrowserView)

    def __init__(self, context, request, attribute=None):
        self.context = context
        self.request = request
        self._page_attribute = attribute

    def __call__(self):
        if hasattr(self, '_page_attribute') and \
           self._page_attribute is not None:
            return getattr(self, self._page_attribute)()
        raise NotImplemented, '__call__ method not implemented'
